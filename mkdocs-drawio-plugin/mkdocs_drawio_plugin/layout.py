"""
Auto-layout engine for diagram IR.

Assigns x/y positions to nodes based on layout direction and topology.
Uses a simple rank-based approach with topological ordering.
"""

from __future__ import annotations

from collections import defaultdict, deque

from .parsers.base import (
    DiagramIR,
    DiagramNode,
    LayoutDirection,
    SequenceParticipant,
)
from . import styles


def _topological_ranks(
    nodes: list[DiagramNode],
    edges: list,
) -> dict[str, int]:
    """Assign rank (layer) to each node via topological sort.

    Nodes with no incoming edges get rank 0, their successors rank 1, etc.
    """
    node_ids = {n.id for n in nodes}
    adj: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {n.id: 0 for n in nodes}

    for e in edges:
        # Skip point-based edges (sequence diagrams)
        if e.source_x is not None:
            continue
        if e.source in node_ids and e.target in node_ids:
            adj[e.source].append(e.target)
            in_degree[e.target] = in_degree.get(e.target, 0) + 1

    # BFS topological sort
    queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
    ranks: dict[str, int] = {}

    while queue:
        nid = queue.popleft()
        rank = ranks.get(nid, 0)
        ranks[nid] = rank
        for neighbor in adj[nid]:
            # Successor rank is at least parent rank + 1
            ranks[neighbor] = max(ranks.get(neighbor, 0), rank + 1)
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Handle any remaining (cycle or disconnected) nodes
    for n in nodes:
        if n.id not in ranks:
            ranks[n.id] = 0

    return ranks


def _group_by_rank(
    nodes: list[DiagramNode],
    ranks: dict[str, int],
) -> dict[int, list[DiagramNode]]:
    """Group nodes into layers by their rank."""
    layers: dict[int, list[DiagramNode]] = defaultdict(list)
    for node in nodes:
        layers[ranks[node.id]].append(node)
    return dict(sorted(layers.items()))


def layout_nodes(ir: DiagramIR) -> None:
    """Assign x/y positions to all nodes in-place.

    Modifies node.x and node.y based on layout direction and topology.
    """
    if not ir.nodes:
        return

    ranks = _topological_ranks(ir.nodes, ir.edges)
    layers = _group_by_rank(ir.nodes, ranks)

    start_x = 50.0
    start_y = 50.0

    if ir.layout == LayoutDirection.TB:
        _layout_tb(layers, start_x, start_y)
    else:
        _layout_lr(layers, start_x, start_y)


def _layout_tb(
    layers: dict[int, list[DiagramNode]],
    start_x: float,
    start_y: float,
) -> None:
    """Top-to-bottom layout: ranks go down, nodes in same rank go across."""
    current_y = start_y

    for rank in sorted(layers.keys()):
        nodes = layers[rank]
        row_width = sum(n.width for n in nodes) + styles.NODE_SPACING_H * (len(nodes) - 1)
        current_x = start_x

        max_height = 0.0
        for node in nodes:
            node.x = current_x
            node.y = current_y
            current_x += node.width + styles.NODE_SPACING_H
            max_height = max(max_height, node.height)

        current_y += max_height + styles.NODE_SPACING_V


def _layout_lr(
    layers: dict[int, list[DiagramNode]],
    start_x: float,
    start_y: float,
) -> None:
    """Left-to-right layout: ranks go right, nodes in same rank go down."""
    current_x = start_x

    for rank in sorted(layers.keys()):
        nodes = layers[rank]
        current_y = start_y

        max_width = 0.0
        for node in nodes:
            node.x = current_x
            node.y = current_y
            current_y += node.height + styles.NODE_SPACING_V
            max_width = max(max_width, node.width)

        current_x += max_width + styles.NODE_SPACING_H


def layout_sequence(ir: DiagramIR) -> None:
    """Layout sequence diagram participants and compute message positions.

    Sets participant x/y, lifeline endpoints, and updates edge coordinates.
    """
    if not ir.participants:
        return

    start_x = 50.0
    participant_y = 30.0

    # Position participants left to right
    current_x = start_x
    participant_centers: dict[str, float] = {}

    for p in ir.participants:
        p.x = current_x
        p.y = participant_y
        p.width = styles.SEQ_PARTICIPANT_WIDTH
        p.height = styles.SEQ_PARTICIPANT_HEIGHT
        center = current_x + p.width / 2
        participant_centers[p.id] = center
        current_x += styles.SEQ_PARTICIPANT_SPACING

    # Compute message y positions
    lifeline_top = participant_y + styles.SEQ_PARTICIPANT_HEIGHT
    msg_y = lifeline_top + styles.SEQ_MESSAGE_Y_START

    for edge in ir.edges:
        if edge.source_x is not None:
            # Already has coordinates — use them (but update y if not set)
            if edge.source_y == 0 and edge.target_y == 0:
                edge.source_y = msg_y
                edge.target_y = msg_y
                msg_y += styles.SEQ_MESSAGE_Y_SPACING
            continue

        # Convert cell-ref edge to point-based edge
        src_x = participant_centers.get(edge.source)
        tgt_x = participant_centers.get(edge.target)
        if src_x is not None and tgt_x is not None:
            edge.source_x = src_x
            edge.source_y = msg_y
            edge.target_x = tgt_x
            edge.target_y = msg_y
            msg_y += styles.SEQ_MESSAGE_Y_SPACING

    # Set lifeline end y to below last message
    lifeline_end = msg_y + 40
    for p in ir.participants:
        p.lifeline_end_y = lifeline_end


def layout_groups(ir: DiagramIR) -> None:
    """Compute group bounds to enclose their child nodes with padding."""
    if not ir.groups:
        return

    for group in ir.groups:
        children = [n for n in ir.nodes if n.parent_group == group.id]
        if not children:
            continue

        min_x = min(n.x for n in children) - styles.GROUP_PADDING
        min_y = min(n.y for n in children) - styles.GROUP_PADDING - 30  # room for label
        max_x = max(n.x + n.width for n in children) + styles.GROUP_PADDING
        max_y = max(n.y + n.height for n in children) + styles.GROUP_PADDING

        group.x = min_x
        group.y = min_y
        group.width = max_x - min_x
        group.height = max_y - min_y

        # Convert child coordinates to relative (within group)
        for child in children:
            child.x -= min_x
            child.y -= min_y


def auto_layout(ir: DiagramIR) -> None:
    """Full auto-layout pipeline for a diagram IR.

    Dispatches to the appropriate layout strategy based on diagram type.
    """
    from .parsers.base import DiagramType

    if ir.diagram_type == DiagramType.SEQUENCE:
        layout_sequence(ir)
    else:
        layout_nodes(ir)
        layout_groups(ir)
