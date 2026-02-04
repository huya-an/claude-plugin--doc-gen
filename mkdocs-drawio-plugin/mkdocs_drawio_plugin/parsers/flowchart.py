"""
Mermaid flowchart parser.

Handles `graph TD`, `graph LR`, `flowchart TD`, `flowchart LR` diagrams.
Parses node definitions, edge connections, and subgraphs.

Uses regex-based line-by-line parsing — no external dependencies.
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

# Match the opening line: graph TD, graph LR, flowchart TD, etc.
_HEADER_RE = re.compile(
    r"^\s*(?:graph|flowchart)\s+(TD|TB|LR|RL|BT)\s*$", re.IGNORECASE
)

# Match subgraph start: subgraph Title
_SUBGRAPH_RE = re.compile(r"^\s*subgraph\s+(.+)$", re.IGNORECASE)

# Match subgraph end
_SUBGRAPH_END_RE = re.compile(r"^\s*end\s*$", re.IGNORECASE)

# Node shapes in Mermaid:
#   id[label]        → rect
#   id(label)        → rounded_rect
#   id([label])      → stadium
#   id[(label)]      → cylinder
#   id((label))      → circle
#   id{label}        → diamond
#   id{{label}}      → hexagon
#   id[/label/]      → parallelogram
#   id>label]        → flag (mapped to rect)

# Edge patterns:
#   --> solid arrow
#   -.-> dotted arrow
#   ==> thick arrow
#   --- solid line (no arrow)
#   -.- dotted line
#   === thick line
#   --text--> labeled solid arrow
#   -.text.-> labeled dotted arrow
#   ==text==> labeled thick arrow
#   -->|text| labeled solid arrow (pipe style)

_EDGE_RE = re.compile(
    r"(\S+)"                    # source node ID
    r"\s*"
    r"("                        # edge operator
    r"-->"                      # solid arrow
    r"|==>"                     # thick arrow
    r"|-\.->|\.->|-\.\.->|\.->" # dotted arrow variants
    r"|---"                     # solid line
    r"|===|-\.-"                # thick/dotted line
    r"|--\s*[^-].*?-->"        # labeled: --text-->
    r"|-\.\s*.*?\.\->"         # labeled: -.text.->
    r"|==\s*.*?==>"            # labeled: ==text==>
    r"|-->\|[^|]*\|"           # labeled: -->|text|
    r")"
    r"\s*"
    r"(\S+)"                    # target node ID
)

# Simpler two-pass approach: first extract node defs, then edges
_NODE_DEF_RE = re.compile(
    r"(?:^|\s)"
    r"([A-Za-z_][A-Za-z0-9_]*)"  # node ID
    r"("
    r"\[\[.*?\]\]"      # double bracket (subroutine)
    r"|\[\(.*?\)\]"     # [(label)] cylinder
    r"|\[\[.*?\]\]"     # [[label]] subroutine
    r"|\[/.*?/\]"       # [/label/] parallelogram
    r"|\[\\.*?\\\]"     # [\label\] parallelogram alt
    r"|\(\[.*?\]\)"     # ([label]) stadium
    r"|\(\(.*?\)\)"     # ((label)) circle
    r"|\{\{.*?\}\}"     # {{label}} hexagon
    r"|\{.*?\}"         # {label} diamond
    r"|\[.*?\]"         # [label] rect
    r"|\(.*?\)"         # (label) rounded_rect
    r"|>.*?\]"          # >label] flag
    r")"
)


def _parse_node_shape(shape_str: str) -> tuple[str, NodeShape]:
    """Extract label text and shape from a Mermaid node shape string."""
    if shape_str.startswith("([") and shape_str.endswith("])"):
        return shape_str[2:-2], NodeShape.STADIUM
    if shape_str.startswith("[(") and shape_str.endswith(")]"):
        return shape_str[2:-2], NodeShape.CYLINDER
    if shape_str.startswith("((") and shape_str.endswith("))"):
        return shape_str[2:-2], NodeShape.CIRCLE
    if shape_str.startswith("{{") and shape_str.endswith("}}"):
        return shape_str[2:-2], NodeShape.HEXAGON
    if shape_str.startswith("{") and shape_str.endswith("}"):
        return shape_str[1:-1], NodeShape.DIAMOND
    if shape_str.startswith("[/") and shape_str.endswith("/]"):
        return shape_str[2:-2], NodeShape.PARALLELOGRAM
    if shape_str.startswith("[") and shape_str.endswith("]"):
        return shape_str[1:-1], NodeShape.RECT
    if shape_str.startswith("(") and shape_str.endswith(")"):
        return shape_str[1:-1], NodeShape.ROUNDED_RECT
    if shape_str.startswith(">") and shape_str.endswith("]"):
        return shape_str[1:-1], NodeShape.RECT
    return shape_str, NodeShape.ROUNDED_RECT


def _classify_edge(operator: str) -> tuple[str, EdgeType]:
    """Classify a Mermaid edge operator and extract any inline label."""
    label = ""

    # Extract label from -->|text| style
    pipe_match = re.search(r"-->\|([^|]*)\|", operator)
    if pipe_match:
        return pipe_match.group(1).strip(), EdgeType.SYNC

    # Extract label from --text--> style
    labeled_solid = re.match(r"--\s*(.+?)\s*-->", operator)
    if labeled_solid:
        return labeled_solid.group(1).strip(), EdgeType.SYNC

    # Extract label from -.text.-> style
    labeled_dotted = re.match(r"-\.\s*(.+?)\s*\.->", operator)
    if labeled_dotted:
        return labeled_dotted.group(1).strip(), EdgeType.ASYNC

    # Extract label from ==text==> style
    labeled_thick = re.match(r"==\s*(.+?)\s*==>", operator)
    if labeled_thick:
        return labeled_thick.group(1).strip(), EdgeType.DATA_FLOW

    # Simple operators
    if "==>" in operator:
        return "", EdgeType.DATA_FLOW
    if ".->" in operator or "-.>" in operator:
        return "", EdgeType.ASYNC
    if "-->" in operator:
        return "", EdgeType.SYNC
    if "---" in operator:
        return "", EdgeType.DEPENDENCY
    if "===" in operator:
        return "", EdgeType.DATA_FLOW
    if "-.-" in operator:
        return "", EdgeType.DEPENDENCY

    return label, EdgeType.SYNC


def parse(text: str) -> DiagramIR:
    """Parse a Mermaid flowchart/graph into DiagramIR."""
    lines = text.strip().splitlines()
    if not lines:
        return DiagramIR(diagram_type=DiagramType.FLOWCHART)

    # Parse header for layout direction
    layout = LayoutDirection.TB
    start_line = 0
    header_match = _HEADER_RE.match(lines[0])
    if header_match:
        direction = header_match.group(1).upper()
        if direction in ("LR", "RL"):
            layout = LayoutDirection.LR
        start_line = 1

    nodes: dict[str, DiagramNode] = {}
    edges: list[DiagramEdge] = []
    groups: list[DiagramGroup] = []
    current_group: str | None = None
    edge_counter = 0
    group_counter = 0

    for line in lines[start_line:]:
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("%%"):
            continue

        # Check subgraph
        sg_match = _SUBGRAPH_RE.match(stripped)
        if sg_match:
            group_counter += 1
            gid = f"group_{group_counter}"
            groups.append(DiagramGroup(
                id=gid,
                label=sg_match.group(1).strip(),
            ))
            current_group = gid
            continue

        if _SUBGRAPH_END_RE.match(stripped):
            current_group = None
            continue

        # Extract node definitions from the line
        for match in _NODE_DEF_RE.finditer(stripped):
            node_id = match.group(1)
            shape_str = match.group(2)
            label, shape = _parse_node_shape(shape_str)

            if node_id not in nodes:
                node = DiagramNode(
                    id=node_id,
                    label=label,
                    shape=shape,
                    parent_group=current_group,
                )
                # Assign default dimensions by shape
                if shape == NodeShape.DIAMOND:
                    node.width = 120
                    node.height = 80
                elif shape == NodeShape.CIRCLE:
                    node.width = 80
                    node.height = 80
                elif shape == NodeShape.START_END:
                    node.width = 100
                    node.height = 40
                nodes[node_id] = node
            else:
                # Update label if re-defined
                nodes[node_id].label = label
                nodes[node_id].shape = shape
                if current_group:
                    nodes[node_id].parent_group = current_group

        # Extract edges from the line
        # Use a more flexible approach: split on edge operators
        _parse_edges_from_line(stripped, nodes, edges, edge_counter, current_group)
        edge_counter = len(edges)

    return DiagramIR(
        diagram_type=DiagramType.FLOWCHART,
        layout=layout,
        nodes=list(nodes.values()),
        edges=edges,
        groups=groups,
    )


def _parse_edges_from_line(
    line: str,
    nodes: dict[str, DiagramNode],
    edges: list[DiagramEdge],
    start_counter: int,
    current_group: str | None,
) -> None:
    """Extract edge connections from a line, handling chained edges."""
    # Pattern: NodeA -->|label| NodeB --> NodeC
    # We need to find all edge operators and their surrounding node IDs

    # Split by common edge operators, keeping delimiters
    edge_ops = re.compile(
        r"(-->\|[^|]*\|"   # -->|label|
        r"|--\s*\S+\s*-->" # --text-->
        r"|==>"             # thick
        r"|\.?-\.->|\.->|-\.\.->|\.->"  # dotted variants
        r"|-->"             # solid
        r"|---"             # line
        r"|===|-\.-)"       # thick line / dotted line
    )

    parts = edge_ops.split(line)
    # parts alternates: [before_op, op, between_op, op, after_op, ...]

    if len(parts) < 3:
        return  # No edge operators found

    i = 0
    while i < len(parts) - 2:
        before = parts[i].strip()
        operator = parts[i + 1]
        after = parts[i + 2].strip()

        # Extract node IDs from before/after text
        src_id = _extract_node_id_end(before)
        tgt_id = _extract_node_id_start(after)

        if src_id and tgt_id:
            # Ensure both nodes exist (create with default if not)
            if src_id not in nodes:
                nodes[src_id] = DiagramNode(
                    id=src_id, label=src_id, parent_group=current_group,
                )
            if tgt_id not in nodes:
                nodes[tgt_id] = DiagramNode(
                    id=tgt_id, label=tgt_id, parent_group=current_group,
                )

            label, edge_type = _classify_edge(operator)
            edge_id = f"e{start_counter + len(edges)}"
            edges.append(DiagramEdge(
                id=edge_id,
                source=src_id,
                target=tgt_id,
                label=label,
                edge_type=edge_type,
            ))

        i += 2  # Move past operator + next text segment


def _extract_node_id_end(text: str) -> str | None:
    """Extract the last node ID from text (before an edge operator)."""
    # Remove any shape definitions to get bare ID
    # Match the last word-like token
    text = text.rstrip()
    # Strip shape suffixes: [label], (label), {label}, etc.
    text = re.sub(r"[\[\(\{<].*?[\]\)\}>]$", "", text).strip()
    # Also handle ((label)), {{label}}, etc.
    text = re.sub(r"[\[\(\{][\[\(\{].*?[\]\)\}][\]\)\}]$", "", text).strip()
    match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", text)
    return match.group(1) if match else None


def _extract_node_id_start(text: str) -> str | None:
    """Extract the first node ID from text (after an edge operator)."""
    text = text.lstrip()
    match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)", text)
    return match.group(1) if match else None
