"""Backend runners for SpinQ / Braket / OriginQ simulators."""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List, Tuple

from .circuit import Circuit
from .emit import (
    emit_braket_native_qasm3,
    emit_braket_qasm3,
    emit_originir,
    emit_spinq_qasm2,
)
from .result import build_result, remap_counts, utc_now


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


def run_originq(circuit: Circuit, shots: int) -> Dict[str, Any]:
    try:
        import pyqpanda as pq
    except ImportError as exc:
        raise ImportError(
            "pyqpanda is required for target=originq. "
            "Install with: pip install pyqpanda"
        ) from exc

    # Prefer feeding OpenQASM 2 (spinq emitter) into pyqpanda converters;
    # OriginIR string is still what transpile() returns for the contract.
    qasm2 = emit_spinq_qasm2(circuit)
    machine = pq.CPUQVM()
    machine.init_qvm()
    try:
        if hasattr(pq, "convert_qasm_string_to_qprog"):
            prog, _qreg, creg = pq.convert_qasm_string_to_qprog(qasm2, machine)
        else:
            prog = pq.convert_qasm_to_qprog(qasm2, machine)
            creg = machine.qAlloc_many(0)  # placeholder; overwritten below
            creg = machine.get_allocate_cbits()
        raw = machine.run_with_configuration(prog, creg, shots)
    finally:
        machine.finalize()

    n_bits, measured = _measure_map(circuit)
    counts = remap_counts(
        raw, n_bits=n_bits, n_qubits=circuit.n_qubits(), measured=measured
    )
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
