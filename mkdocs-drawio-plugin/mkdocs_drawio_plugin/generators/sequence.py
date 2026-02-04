"""
Sequence diagram generator — converts sequence DiagramIR to draw.io XML.

CRITICAL: Message arrows use explicit sourcePoint/targetPoint coordinates,
NOT source/target cell ID references. Using cell ID references causes
arrows to connect to participant header boxes, producing broken diagrams.
"""

from __future__ import annotations

from ..parsers.base import DiagramIR
from ..layout import layout_sequence
from .base import ir_to_xml


def generate(ir: DiagramIR) -> str:
    """Generate draw.io XML from a sequence DiagramIR.

    Handles participant positioning, lifelines, and point-based message edges.
    """
    layout_sequence(ir)
    return ir_to_xml(ir)
