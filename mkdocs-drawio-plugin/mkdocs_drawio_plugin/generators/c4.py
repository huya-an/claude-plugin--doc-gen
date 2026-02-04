"""
C4 diagram generator — converts C4 DiagramIR to draw.io XML.

Uses the base ir_to_xml with appropriate styling per C4 level.
"""

from __future__ import annotations

from ..parsers.base import DiagramIR
from ..layout import auto_layout
from .base import ir_to_xml


def generate(ir: DiagramIR) -> str:
    """Generate draw.io XML from a C4 DiagramIR."""
    auto_layout(ir)
    return ir_to_xml(ir)
