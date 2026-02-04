"""
Mermaid C4 diagram parser.

Handles C4Context, C4Container, C4Component, and C4Dynamic diagrams
using the Mermaid C4 extension syntax.

Supported elements:
  Person(alias, label, descr)
  System(alias, label, descr)
  System_Ext(alias, label, descr)
  Container(alias, label, techn, descr)
  ContainerDb(alias, label, techn, descr)
  ContainerQueue(alias, label, techn, descr)
  Component(alias, label, techn, descr)
  Rel(from, to, label, techn)
  BiRel(from, to, label, techn)
  Boundary(alias, label) { ... }
  System_Boundary(alias, label) { ... }
  Container_Boundary(alias, label) { ... }
"""

from __future__ import annotations

import re

from .base import (
    DiagramEdge,
    DiagramGroup,
    DiagramIR,
    DiagramNode,
    DiagramType,
    EdgeType,
    LayoutDirection,
    NodeShape,
)

# Header patterns
_HEADER_MAP = {
    "c4context": DiagramType.C4_CONTEXT,
    "c4container": DiagramType.C4_CONTAINER,
    "c4component": DiagramType.C4_COMPONENT,
    "c4dynamic": DiagramType.C4_CONTEXT,  # treat dynamic as context layout
    "c4deployment": DiagramType.C4_CONTEXT,
}

_HEADER_RE = re.compile(
    r"^\s*(C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\s*$",
    re.IGNORECASE,
)

# Element patterns — capture comma-separated args in parens
_ELEMENT_RE = re.compile(
    r"^\s*(Person|Person_Ext|System|System_Ext|SystemDb|SystemQueue|"
    r"Container|ContainerDb|ContainerQueue|"
    r"Component|ComponentDb|ComponentQueue)"
    r"\s*\((.+)\)\s*$",
    re.IGNORECASE,
)

# Relationship patterns
_REL_RE = re.compile(
    r"^\s*(Rel|BiRel|Rel_Back|Rel_Neighbor|Rel_D|Rel_U|Rel_L|Rel_R)"
    r"\s*\((.+)\)\s*$",
    re.IGNORECASE,
)

# Boundary patterns
_BOUNDARY_RE = re.compile(
    r"^\s*(Boundary|System_Boundary|Container_Boundary|Enterprise_Boundary)"
    r"\s*\(([^,]+),\s*(.+)\)\s*\{\s*$",
    re.IGNORECASE,
)

_BOUNDARY_END_RE = re.compile(r"^\s*\}\s*$")

# UpdateRelStyle, UpdateElementStyle, etc. — skip these
_STYLE_RE = re.compile(r"^\s*Update(Rel|Element|Layout)Style\s*\(", re.IGNORECASE)


def _split_args(args_str: str) -> list[str]:
    """Split comma-separated args, respecting quoted strings."""
    args = []
    current = []
    in_quotes = False
    quote_char = None

    for ch in args_str:
        if ch in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = ch
        elif ch == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
        elif ch == "," and not in_quotes:
            args.append("".join(current).strip().strip("\"'"))
            current = []
            continue
        current.append(ch)

    if current:
        args.append("".join(current).strip().strip("\"'"))
    return args


def _element_to_node(elem_type: str, args: list[str]) -> DiagramNode:
    """Convert a C4 element declaration to a DiagramNode."""
    alias = args[0] if args else "unknown"
    label = args[1] if len(args) > 1 else alias
    techn = args[2] if len(args) > 2 else ""
    descr = args[3] if len(args) > 3 else ""

    lower = elem_type.lower()

    # Determine shape and semantic role
    shape = NodeShape.ROUNDED_RECT
    role = "compute"

    if "person" in lower:
        shape = NodeShape.PERSON
        role = "person"
    elif "db" in lower:
        shape = NodeShape.CYLINDER
        role = "database"
    elif "queue" in lower:
        shape = NodeShape.ROUNDED_RECT
        role = "queue"
    elif "_ext" in lower or "ext" in lower:
        role = "external"

    # Build multi-line label: name + [technology] + description
    parts = [f"<b>{label}</b>"]
    if techn:
        parts.append(f"[{techn}]")
    if descr:
        parts.append(descr)
    display_label = "&#xa;".join(parts)

    return DiagramNode(
        id=alias,
        label=display_label,
        shape=shape,
        semantic_role=role,
    )


def parse(text: str) -> DiagramIR:
    """Parse a Mermaid C4 diagram into DiagramIR."""
    lines = text.strip().splitlines()
    if not lines:
        return DiagramIR(diagram_type=DiagramType.C4_CONTEXT)

    # Detect diagram type from header
    diagram_type = DiagramType.C4_CONTEXT
    start_line = 0
    header_match = _HEADER_RE.match(lines[0])
    if header_match:
        key = header_match.group(1).lower()
        diagram_type = _HEADER_MAP.get(key, DiagramType.C4_CONTEXT)
        start_line = 1

    nodes: dict[str, DiagramNode] = {}
    edges: list[DiagramEdge] = []
    groups: list[DiagramGroup] = []
    boundary_stack: list[str] = []
    edge_counter = 0
    group_counter = 0

    for line in lines[start_line:]:
        stripped = line.strip()

        if not stripped or stripped.startswith("%%"):
            continue

        # Skip style update directives
        if _STYLE_RE.match(stripped):
            continue

        # Boundary start
        b_match = _BOUNDARY_RE.match(stripped)
        if b_match:
            group_counter += 1
            alias = b_match.group(2).strip().strip("\"'")
            label = b_match.group(3).strip().strip("\"'")
            gid = f"boundary_{alias}"
            groups.append(DiagramGroup(
                id=gid,
                label=label,
                group_type="info",
            ))
            boundary_stack.append(gid)
            continue

        # Boundary end
        if _BOUNDARY_END_RE.match(stripped):
            if boundary_stack:
                boundary_stack.pop()
            continue

        # Element
        e_match = _ELEMENT_RE.match(stripped)
        if e_match:
            elem_type = e_match.group(1)
            args = _split_args(e_match.group(2))
            node = _element_to_node(elem_type, args)
            if boundary_stack:
                node.parent_group = boundary_stack[-1]
            nodes[node.id] = node
            continue

        # Relationship
        r_match = _REL_RE.match(stripped)
        if r_match:
            rel_type = r_match.group(1).lower()
            args = _split_args(r_match.group(2))
            if len(args) >= 2:
                src = args[0]
                tgt = args[1]
                label = args[2] if len(args) > 2 else ""
                techn = args[3] if len(args) > 3 else ""

                if techn:
                    label = f"{label} [{techn}]"

                edge_type = EdgeType.SYNC
                if "back" in rel_type:
                    src, tgt = tgt, src

                edge_id = f"rel_{edge_counter}"
                edge_counter += 1
                edges.append(DiagramEdge(
                    id=edge_id,
                    source=src,
                    target=tgt,
                    label=label.strip(),
                    edge_type=edge_type,
                ))
            continue

    return DiagramIR(
        diagram_type=diagram_type,
        layout=LayoutDirection.TB,
        nodes=list(nodes.values()),
        edges=edges,
        groups=groups,
    )
