"""
Orchestrator: detect Mermaid diagram type → parse → generate → encode.

This is the main entry point for converting Mermaid text to draw.io HTML.
"""

from __future__ import annotations

import re

from .parsers.base import DiagramIR, DiagramType
from .parsers import flowchart, sequence, c4, erd, generic
from .generators import flowchart as gen_flowchart
from .generators import sequence as gen_sequence
from .generators import c4 as gen_c4
from .generators import erd as gen_erd
from .generators import generic as gen_generic
from .encoding import encode_for_mxgraph, wrap_in_mxgraph_div


def detect_type(text: str) -> DiagramType:
    """Detect the Mermaid diagram type from its first meaningful line."""
    for line in text.strip().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue

        lower = stripped.lower()

        if lower.startswith(("graph ", "flowchart ")):
            return DiagramType.FLOWCHART
        if lower == "sequencediagram":
            return DiagramType.SEQUENCE
        if lower.startswith("c4context"):
            return DiagramType.C4_CONTEXT
        if lower.startswith("c4container"):
            return DiagramType.C4_CONTAINER
        if lower.startswith("c4component"):
            return DiagramType.C4_COMPONENT
        if lower.startswith("c4"):
            return DiagramType.C4_CONTEXT
        if lower == "erdiagram":
            return DiagramType.ERD

        break  # Only check first meaningful line

    return DiagramType.GENERIC


# Type → (parser, generator) dispatch
_DISPATCH = {
    DiagramType.FLOWCHART: (flowchart.parse, gen_flowchart.generate),
    DiagramType.SEQUENCE: (sequence.parse, gen_sequence.generate),
    DiagramType.C4_CONTEXT: (c4.parse, gen_c4.generate),
    DiagramType.C4_CONTAINER: (c4.parse, gen_c4.generate),
    DiagramType.C4_COMPONENT: (c4.parse, gen_c4.generate),
    DiagramType.C4_CODE: (c4.parse, gen_c4.generate),
    DiagramType.ERD: (erd.parse, gen_erd.generate),
    DiagramType.GENERIC: (generic.parse, gen_generic.generate),
}


def mermaid_to_ir(text: str) -> DiagramIR:
    """Parse Mermaid text into an intermediate representation."""
    dtype = detect_type(text)
    parser, _ = _DISPATCH[dtype]
    return parser(text)


def ir_to_xml(ir: DiagramIR) -> str:
    """Generate draw.io XML from a DiagramIR."""
    _, generator = _DISPATCH[ir.diagram_type]
    return generator(ir)


def mermaid_to_xml(text: str) -> str:
    """Convert Mermaid text to raw draw.io XML."""
    ir = mermaid_to_ir(text)
    return ir_to_xml(ir)


def mermaid_to_html(text: str) -> str:
    """Convert Mermaid text to an embeddable draw.io HTML div.

    This is the primary entry point used by the MkDocs plugin.
    """
    xml = mermaid_to_xml(text)
    encoded = encode_for_mxgraph(xml)
    return wrap_in_mxgraph_div(encoded)


def mermaid_to_figure(text: str, caption: str = "") -> str:
    """Convert Mermaid text to a <figure> element with draw.io embed.

    Wraps the diagram div in a <figure> with optional <figcaption>.
    """
    div = mermaid_to_html(text)

    parts = ['<figure class="drawio-diagram">']
    parts.append(f"  {div}")
    if caption:
        parts.append(f"  <figcaption>{caption}</figcaption>")
    parts.append("</figure>")

    return "\n".join(parts)
