"""
Generic fallback parser for unrecognized Mermaid diagram types.

Creates a simple single-node diagram with the raw Mermaid source
as the label, so the content isn't silently lost.
"""

from __future__ import annotations

from .base import (
    DiagramIR,
    DiagramNode,
    DiagramType,
    NodeShape,
)


def parse(text: str) -> DiagramIR:
    """Parse unrecognized Mermaid syntax into a minimal DiagramIR.

    Creates a single node containing the raw source text.
    """
    # Try to extract the first line as a title
    lines = text.strip().splitlines()
    title = lines[0].strip() if lines else "Diagram"

    # Truncate long content for the label
    preview = text.strip()
    if len(preview) > 200:
        preview = preview[:200] + "..."

    node = DiagramNode(
        id="generic_1",
        label=preview.replace("\n", "&#xa;"),
        shape=NodeShape.RECT,
        width=400,
        height=max(100, len(lines) * 16),
    )

    return DiagramIR(
        diagram_type=DiagramType.GENERIC,
        title=title,
        nodes=[node],
    )
