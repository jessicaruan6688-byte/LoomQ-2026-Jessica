#!/usr/bin/env python3
"""LoomQ submission adapter contract v1.0.

Implements a unified OpenQASM 2.0 middle layer with SpinQ / OriginQ / Braket
emitters and simulator runners. L2/L3 remain optional stubs.
"""

from typing import Any, Dict, List, Tuple

from loomq import compile_hybrid as _compile_hybrid
from loomq import run_circuit, transpile_circuit

SUPPORTED_TARGETS = ("spinq", "originq", "braket")


def transpile(qasm_str: str, target: str) -> str:
    """Translate OpenQASM 2.0 into the target backend's native representation."""
    return transpile_circuit(qasm_str, target)


def run(qasm_str: str, target: str, shots: int) -> Dict[str, Any]:
    """Execute a circuit and return the unified result schema from the rules."""
    return run_circuit(qasm_str, target, shots)


def agent_chat(prompt: str) -> str:
    """Optional L2 entry point using the documented LOOMQ_LLM_* environment."""
    raise NotImplementedError("L2 is optional; implement agent_chat(prompt) to enter")


def compile_hybrid(hybrid_qasm_str: str) -> Tuple[List[str], str]:
    """Optional L3 entry point. Return quantum operations and RISC-V assembly."""
    return _compile_hybrid(hybrid_qasm_str)
