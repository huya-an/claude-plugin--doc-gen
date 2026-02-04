"""
Flowchart generator — converts flowchart DiagramIR to draw.io XML.

Uses the base ir_to_xml function since flowcharts follow the standard
node+edge pattern without special handling.
"""

from __future__ import annotations

from ..parsers.base import DiagramIR
from ..layout import auto_layout
from .base import ir_to_xml


def generate(ir: DiagramIR) -> str:
    """Generate draw.io XML from a flowchart DiagramIR."""
    auto_layout(ir)
    return ir_to_xml(ir)
