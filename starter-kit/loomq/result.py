"""Unified LoomQ result schema helpers.

Bit order is normalised in exactly one place, here, because the backends and the
competition schema disagree twice over:

* SDKs key their counts by **qubit** index, leftmost character = ``q[0]``, and
  they ignore the measure map, so ``measure q[1] -> c[0]`` still reports the bit
  in q1's slot.
* The unified schema is ``bit_order: "little"`` and keyed by **classical** bit,
  so ``c[0]`` is the rightmost character and the measure map must be honoured.

Bell and GHZ are symmetric under bit reversal, which makes this class of bug
invisible on the public circuits; every asymmetric circuit exposes it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_bitstring(key: Any, width: int) -> str:
    if isinstance(key, int) and not isinstance(key, bool):
        return format(key, f"0{width}b")
    text = str(key).strip()
    cleaned = "".join(ch for ch in text if ch in "01")
    if cleaned and len(cleaned) == len(text.replace(" ", "")):
        return cleaned
    if text.isdigit():
        return format(int(text), f"0{width}b")
    if not cleaned:
        raise ValueError(f"cannot interpret counts key: {key!r}")
    return cleaned


def remap_counts(
    counts: Mapping[Any, Any],
    *,
    n_bits: int,
    n_qubits: int,
    measured: Sequence[Tuple[int, int]],
) -> Dict[str, int]:
    """Rewrite qubit-indexed backend counts into little-endian classical bits.

    ``measured`` holds ``(qubit_index, cbit_index)`` pairs taken from the circuit's
    measure statements.
    """
    qubit_to_cbit: Dict[int, int] = {}
    for qubit_index, cbit_index in measured:
        qubit_to_cbit[qubit_index] = cbit_index
    measured_qubits = sorted(qubit_to_cbit)

    out: Dict[str, int] = {}
    for key, value in counts.items():
        bits = _as_bitstring(key, n_qubits)
        if len(bits) == n_qubits:
            source = list(range(n_qubits))
        elif len(bits) == len(measured_qubits):
            source = measured_qubits
        else:
            raise ValueError(
                f"counts key {key!r} has width {len(bits)}, expected "
                f"{n_qubits} or {len(measured_qubits)}"
            )
        target = ["0"] * n_bits
        for position, qubit_index in enumerate(source):
            cbit = qubit_to_cbit.get(qubit_index)
            if cbit is None:
                continue
            target[n_bits - 1 - cbit] = bits[position]
        bitstring = "".join(target)
        out[bitstring] = out.get(bitstring, 0) + int(value)
    return out


def build_result(
    *,
    backend: str,
    job_id: str,
    shots: int,
    counts: Mapping[str, int],
    meta: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Assemble the unified schema from counts already keyed by classical bit."""
    normalized = {str(key): int(value) for key, value in counts.items()}
    total = sum(normalized.values())
    if total == 0:
        raise ValueError("backend returned empty counts")
    if total != shots:
        raise ValueError(f"counts total {total} != shots {shots}")
    return {
        "backend": backend,
        "job_id": str(job_id),
        "shots": int(shots),
        "counts": normalized,
        "bit_order": "little",
        "timestamp": timestamp or utc_now(),
        "meta": meta or {},
    }
