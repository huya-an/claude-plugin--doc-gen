"""
Generic fallback generator — wraps unrecognized content in a simple box.
"""

from __future__ import annotations

from ..parsers.base import DiagramIR
from ..layout import auto_layout
from .base import ir_to_xml


def generate(ir: DiagramIR) -> str:
    """Generate draw.io XML from a generic DiagramIR."""
    auto_layout(ir)
    return ir_to_xml(ir)
