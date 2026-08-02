"""Backend runners for SpinQ / Braket / OriginQ simulators."""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .circuit import Circuit
from .emit import (
    emit_braket_native_qasm3,
    emit_braket_qasm3,
    emit_originir,
    emit_spinq_qasm2,
)
from .result import build_result, normalize_classical_counts, remap_counts, utc_now


def _measure_map(circuit: Circuit) -> Tuple[int, List[Tuple[int, int]]]:
    """Return the output width and the (qubit, cbit) pairs the circuit measures."""
    measured = [
        (circuit.qubit_index(op.qubit), circuit.cbit_index(op.cbit))
        for op in circuit.measure_ops()
    ]
    if measured:
        return circuit.n_clbits(), measured
    # An unmeasured circuit is reported as if every qubit mapped to its own bit.
    n = circuit.n_qubits()
    return n, [(index, index) for index in range(n)]


def run_spinq(circuit: Circuit, shots: int) -> Dict[str, Any]:
    try:
        from spinqit import BasicSimulatorConfig, get_basic_simulator, get_compiler
    except ImportError as exc:
        raise ImportError(
            "spinqit is required for target=spinq. "
            "Install with: pip install spinqit==0.2.4"
        ) from exc

    qasm = emit_spinq_qasm2(circuit)
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".qasm", delete=False, encoding="utf-8"
    )
    try:
        tmp.write(qasm)
        tmp.close()
        compiler = get_compiler("qasm")
        ir = compiler.compile(tmp.name, 0)
    finally:
        os.unlink(tmp.name)

    engine = get_basic_simulator()
    config = BasicSimulatorConfig()
    config.configure_shots(shots)
    result = engine.execute(ir, config)
    raw = getattr(result, "counts", None)
    if raw is None:
        raise RuntimeError("spinqit result has no counts")

    n_bits, measured = _measure_map(circuit)
    counts = remap_counts(
        raw, n_bits=n_bits, n_qubits=circuit.n_qubits(), measured=measured
    )
    job_id = (
        getattr(result, "job_id", None)
        or getattr(result, "task_id", None)
        or f"spinq-local-{abs(hash(qasm)) % 10_000_000:07d}"
    )
    return build_result(
        backend="spinq_basic_simulator",
        job_id=str(job_id),
        shots=shots,
        counts=counts,
        meta={
            "transpiled_gates": len(circuit.gate_ops()),
            "qubits": circuit.n_qubits(),
            "target_ir": "openqasm2",
        },
    )


def run_braket(circuit: Circuit, shots: int) -> Dict[str, Any]:
    try:
        from braket.devices import LocalSimulator
        from braket.ir.openqasm import Program
    except ImportError as exc:
        raise ImportError(
            "amazon-braket-sdk is required for target=braket. "
            "Install with: pip install amazon-braket-sdk==1.50.0"
        ) from exc

    qasm3 = emit_braket_native_qasm3(circuit)
    device = LocalSimulator()
    program = Program(source=qasm3)
    task = device.run(program, shots=shots)
    result = task.result()
    n_bits, measured = _measure_map(circuit)
    counts = remap_counts(
        dict(result.measurement_counts),
        n_bits=n_bits,
        n_qubits=circuit.n_qubits(),
        measured=measured,
    )

    job_id = getattr(getattr(result, "task_metadata", None), "id", None) or f"braket-local-{abs(hash(qasm3)) % 10_000_000:07d}"
    timestamp = utc_now()
    try:
        start = result.additional_metadata.action.startTime
        if start is not None:
            timestamp = str(start)
    except Exception:  # noqa: BLE001
        pass

    return build_result(
        backend="braket_local_simulator",
        job_id=str(job_id),
        shots=shots,
        counts=counts,
        timestamp=timestamp,
        meta={
            "transpiled_gates": len(circuit.gate_ops()),
            "qubits": circuit.n_qubits(),
            "target_ir": "openqasm3",
        },
    )


def _originq_api_token() -> Optional[str]:
    return (
        os.environ.get("LOOMQ_ORIGINQ_API_KEY")
        or os.environ.get("ORIGINQ_API_KEY")
        or os.environ.get("QCLOUD_API_TOKEN")
        or ""
    ).strip() or None


def _originq_wants_cloud() -> bool:
    mode = (os.environ.get("LOOMQ_ORIGINQ_MODE") or "local").strip().lower()
    return mode in {"wukong", "cloud", "qpu", "real", "chip"}


def _probs_to_counts(raw: Mapping[Any, Any], shots: int, n_bits: int) -> Dict[str, int]:
    """Convert cloud probability maps (or already-integer counts) into shot counts."""
    items: List[Tuple[str, float]] = []
    for key, value in raw.items():
        bits = str(key).strip()
        cleaned = "".join(ch for ch in bits if ch in "01")
        if cleaned and set(bits.replace(" ", "")) <= {"0", "1"}:
            bitstring = cleaned.zfill(n_bits)[-n_bits:]
        elif str(key).isdigit():
            bitstring = format(int(key), f"0{n_bits}b")
        else:
            bitstring = cleaned.zfill(n_bits)[-n_bits:] if cleaned else bits
        items.append((bitstring, float(value)))

    total = sum(weight for _, weight in items)
    if total <= 0:
        raise ValueError("originq cloud returned empty measurement payload")

    # Values already look like shot counts.
    if abs(total - shots) <= max(1, shots * 0.01) and all(
        abs(weight - round(weight)) < 1e-6 for _, weight in items
    ):
        return normalize_classical_counts(
            {key: int(round(weight)) for key, weight in items}, n_bits
        )

    # Largest-remainder so the integers sum to shots exactly.
    scaled = [(key, weight / total * shots) for key, weight in items]
    floors = [(key, int(value)) for key, value in scaled]
    remainders = sorted(
        ((value - floor, key) for (key, value), (_, floor) in zip(scaled, floors)),
        reverse=True,
    )
    assigned = {key: floor for key, floor in floors}
    missing = shots - sum(assigned.values())
    for index in range(missing):
        assigned[remainders[index % len(remainders)][1]] += 1
    return normalize_classical_counts(assigned, n_bits)


def _qprog_from_qasm(pq: Any, machine: Any, qasm2: str) -> Any:
    converted = pq.convert_qasm_string_to_qprog(qasm2, machine)
    if isinstance(converted, (list, tuple)):
        return converted[0]
    return converted


def run_originq_local(circuit: Circuit, shots: int) -> Dict[str, Any]:
    try:
        import pyqpanda as pq
    except ImportError as exc:
        raise ImportError(
            "pyqpanda is required for target=originq. "
            "Install with: pip install pyqpanda"
        ) from exc

    # Feed OpenQASM 2 into pyqpanda; OriginIR remains what transpile() returns.
    # pyqpanda already returns classical little-endian keys that honour the
    # measure map, so remapping as if they were qubit-indexed would corrupt them.
    qasm2 = emit_spinq_qasm2(circuit)
    machine = pq.CPUQVM()
    machine.init_qvm()
    try:
        converted = pq.convert_qasm_string_to_qprog(qasm2, machine)
        if isinstance(converted, (list, tuple)) and len(converted) >= 3:
            prog, _qreg, creg = converted[0], converted[1], converted[2]
        elif isinstance(converted, (list, tuple)):
            prog = converted[0]
            creg = machine.get_allocate_cbits()
        else:
            prog = converted
            creg = machine.get_allocate_cbits()
        raw = machine.run_with_configuration(prog, creg, shots)
    finally:
        machine.finalize()

    n_bits, _measured = _measure_map(circuit)
    counts = normalize_classical_counts(raw, n_bits)
    return build_result(
        backend="originq_cpu_simulator",
        job_id=f"originq-sim-{abs(hash(qasm2)) % 10_000_000:07d}",
        shots=shots,
        counts=counts,
        meta={
            "transpiled_gates": len(circuit.gate_ops()),
            "qubits": circuit.n_qubits(),
            "target_ir": "originir",
            "originir_preview": emit_originir(circuit).splitlines()[:8],
        },
    )


def run_originq_wukong(circuit: Circuit, shots: int) -> Dict[str, Any]:
    """Submit to Origin Wukong via QCloud when LOOMQ_ORIGINQ_MODE=wukong."""
    token = _originq_api_token()
    if not token:
        raise RuntimeError(
            "LOOMQ_ORIGINQ_MODE requests the Wukong chip but no API key is set. "
            "Export LOOMQ_ORIGINQ_API_KEY (from console.originqc.com.cn API Key)."
        )
    try:
        import pyqpanda as pq
    except ImportError as exc:
        raise ImportError(
            "pyqpanda is required for OriginQ cloud execution. "
            "Install with: pip install pyqpanda"
        ) from exc

    qasm2 = emit_spinq_qasm2(circuit)
    originir = emit_originir(circuit)
    machine = pq.QCloud()
    if hasattr(machine, "set_configure"):
        machine.set_configure(72, 72)
    machine.init_qvm(token, False)
    chip = getattr(pq.real_chip_type, "origin_72", 2)
    job_id = None
    try:
        # Prefer OriginIR when the cloud accepts strings; fall back to QProg.
        payload: Any = originir
        try:
            if hasattr(machine, "async_real_chip_measure"):
                job_id = machine.async_real_chip_measure(
                    payload, shots, chip_id=chip, task_name="LoomQ-L1"
                )
            else:
                raw = machine.real_chip_measure(
                    payload, shots, chip_id=chip, task_name="LoomQ-L1"
                )
        except Exception:
            prog = _qprog_from_qasm(pq, machine, qasm2)
            if hasattr(machine, "async_real_chip_measure"):
                job_id = machine.async_real_chip_measure(
                    prog, shots, chip_id=chip, task_name="LoomQ-L1"
                )
            else:
                raw = machine.real_chip_measure(
                    prog, shots, chip_id=chip, task_name="LoomQ-L1"
                )
                job_id = None

        if job_id is not None:
            # Poll until the cloud returns a terminal payload.
            raw = None
            status_fn = getattr(machine, "query_task_state_result", None)
            if status_fn is None:
                raise RuntimeError(
                    f"submitted Wukong task {job_id!r} but query_task_state_result is unavailable"
                )
            import time

            deadline = time.time() + int(os.environ.get("LOOMQ_ORIGINQ_TIMEOUT_SEC", "1800"))
            while time.time() < deadline:
                state_payload = status_fn(str(job_id), True)
                if isinstance(state_payload, tuple) and len(state_payload) >= 2:
                    state, raw = state_payload[0], state_payload[1]
                    finished = getattr(getattr(pq.QCloud, "TaskStatus", object), "FINISHED", None)
                    finished_value = getattr(finished, "value", 0)
                    if state == finished_value or raw:
                        break
                elif isinstance(state_payload, dict):
                    raw = state_payload
                    break
                time.sleep(5)
            if raw is None:
                raise TimeoutError(f"OriginQ Wukong task {job_id} timed out")
    finally:
        if hasattr(machine, "finalize"):
            machine.finalize()

    n_bits, _measured = _measure_map(circuit)
    counts = _probs_to_counts(raw, shots, n_bits)
    return build_result(
        backend="originq_wukong",
        job_id=str(job_id or f"originq-wukong-{abs(hash(originir)) % 10_000_000:07d}"),
        shots=shots,
        counts=counts,
        meta={
            "transpiled_gates": len(circuit.gate_ops()),
            "qubits": circuit.n_qubits(),
            "target_ir": "originir",
            "chip": "origin_72",
            "mode": "wukong",
        },
    )


def run_originq(circuit: Circuit, shots: int) -> Dict[str, Any]:
    if _originq_wants_cloud():
        return run_originq_wukong(circuit, shots)
    return run_originq_local(circuit, shots)


RUNNERS = {
    "spinq": run_spinq,
    "braket": run_braket,
    "originq": run_originq,
}


def run_backend(circuit: Circuit, target: str, shots: int) -> Dict[str, Any]:
    if target not in RUNNERS:
        raise ValueError(f"unsupported target '{target}'")
    if not isinstance(shots, int) or isinstance(shots, bool) or shots <= 0:
        raise ValueError("shots must be a positive int")
    return RUNNERS[target](circuit, shots)
