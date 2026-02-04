"""
Shared XML cell builders for draw.io mxGraph generation.

All generators use these primitives to build mxCell elements.
The final XML wraps cells in <mxGraphModel><root>...</root></mxGraphModel>.
"""

from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from ..parsers.base import (
    DiagramEdge,
    DiagramGroup,
    DiagramIR,
    DiagramNode,
    EdgeType,
    NodeShape,
    SequenceParticipant,
)
from .. import styles


def _resolve_node_style(node: DiagramNode) -> str:
    """Resolve the style string for a node."""
    if node.style_override:
        return node.style_override

    # Check semantic role first
    if node.semantic_role and node.semantic_role in styles.NODE_STYLES:
        return styles.NODE_STYLES[node.semantic_role]

    # Map shape to style
    shape_map = {
        NodeShape.DIAMOND: styles.SHAPE_DECISION,
        NodeShape.START_END: styles.SHAPE_START_END,
        NodeShape.ERROR_END: styles.SHAPE_ERROR_END,
        NodeShape.PARALLELOGRAM: styles.SHAPE_PARALLELOGRAM,
        NodeShape.HEXAGON: styles.SHAPE_HEXAGON,
        NodeShape.UML_CLASS: styles.SHAPE_UML_CLASS,
        NodeShape.CYLINDER: styles.NODE_DATABASE,
        NodeShape.PERSON: styles.NODE_PERSON,
        NodeShape.CIRCLE: styles.SHAPE_START_END,
    }

    if node.shape in shape_map:
        return shape_map[node.shape]

    # Default: compute style
    return styles.NODE_COMPUTE


def _resolve_edge_style(edge: DiagramEdge) -> str:
    """Resolve the style string for an edge."""
    if edge.style_override:
        return edge.style_override

    type_key = edge.edge_type.value
    return styles.EDGE_STYLES.get(type_key, styles.EDGE_SYNC)


def build_vertex_cell(
    cell_id: str,
    value: str,
    style: str,
    x: float,
    y: float,
    width: float,
    height: float,
    parent: str = "1",
) -> Element:
    """Build an mxCell element for a vertex (shape/box)."""
    cell = Element("mxCell")
    cell.set("id", cell_id)
    cell.set("value", value)
    cell.set("style", style)
    cell.set("vertex", "1")
    cell.set("parent", parent)

    geo = SubElement(cell, "mxGeometry")
    geo.set("x", str(x))
    geo.set("y", str(y))
    geo.set("width", str(width))
    geo.set("height", str(height))
    geo.set("as", "geometry")

    return cell


def build_edge_cell(
    cell_id: str,
    value: str,
    style: str,
    source_id: str,
    target_id: str,
    parent: str = "1",
) -> Element:
    """Build an mxCell element for an edge using source/target cell IDs."""
    cell = Element("mxCell")
    cell.set("id", cell_id)
    cell.set("value", value)
    cell.set("style", style)
    cell.set("edge", "1")
    cell.set("source", source_id)
    cell.set("target", target_id)
    cell.set("parent", parent)

    geo = SubElement(cell, "mxGeometry")
    geo.set("relative", "1")
    geo.set("as", "geometry")

    return cell


def build_point_edge_cell(
    cell_id: str,
    value: str,
    style: str,
    source_x: float,
    source_y: float,
    target_x: float,
    target_y: float,
    parent: str = "1",
) -> Element:
    """Build an mxCell edge using explicit sourcePoint/targetPoint coordinates.

    Used for sequence diagram messages where cell ID references would
    incorrectly connect to participant header boxes.
    """
    cell = Element("mxCell")
    cell.set("id", cell_id)
    cell.set("value", value)
    cell.set("style", style)
    cell.set("edge", "1")
    cell.set("parent", parent)

    geo = SubElement(cell, "mxGeometry")
    geo.set("relative", "1")
    geo.set("as", "geometry")

    src_point = SubElement(geo, "mxPoint")
    src_point.set("x", str(source_x))
    src_point.set("y", str(source_y))
    src_point.set("as", "sourcePoint")

    tgt_point = SubElement(geo, "mxPoint")
    tgt_point.set("x", str(target_x))
    tgt_point.set("y", str(target_y))
    tgt_point.set("as", "targetPoint")

    return cell


def build_group_cell(
    cell_id: str,
    value: str,
    style: str,
    x: float,
    y: float,
    width: float,
    height: float,
    parent: str = "1",
) -> Element:
    """Build an mxCell for a group/container."""
    cell = Element("mxCell")
    cell.set("id", cell_id)
    cell.set("value", value)
    cell.set("style", style)
    cell.set("vertex", "1")
    cell.set("parent", parent)

    geo = SubElement(cell, "mxGeometry")
    geo.set("x", str(x))
    geo.set("y", str(y))
    geo.set("width", str(width))
    geo.set("height", str(height))
    geo.set("as", "geometry")

    return cell


def ir_to_xml(ir: DiagramIR) -> str:
    """Convert a DiagramIR to mxGraphModel XML string.

    This is the default generator that handles most diagram types.
    Specialized generators (sequence, ERD) override this for type-specific logic.
    """
    root_elem = Element("mxGraphModel")
    root = SubElement(root_elem, "root")

    # Reserved cells
    cell0 = SubElement(root, "mxCell")
    cell0.set("id", "0")
    cell1 = SubElement(root, "mxCell")
    cell1.set("id", "1")
    cell1.set("parent", "0")

    # Groups first (so they render behind nodes)
    for group in ir.groups:
        style = group.style_override or styles.GROUP_STYLES.get(
            group.group_type, styles.GROUP_SUCCESS
        )
        cell = build_group_cell(
            group.id, group.label, style,
            group.x, group.y, group.width, group.height,
        )
        root.append(cell)

    # Vertices
    for node in ir.nodes:
        style = _resolve_node_style(node)
        parent = node.parent_group if node.parent_group else "1"
        cell = build_vertex_cell(
            node.id, node.label, style,
            node.x, node.y, node.width, node.height,
            parent=parent,
        )
        root.append(cell)

    # Sequence participants + lifelines
    for p in ir.participants:
        p_style = styles.NODE_STYLES.get(p.semantic_role or "compute", styles.NODE_COMPUTE)
        p_style = p_style.rstrip(";") + ";fontStyle=1;fontSize=11;"
        cell = build_vertex_cell(
            p.id, p.label, p_style,
            p.x, p.y, p.width, p.height,
        )
        root.append(cell)

        # Lifeline edge
        center_x = p.x + p.width / 2
        lifeline_top = p.y + p.height
        lifeline = build_point_edge_cell(
            f"{p.id}_lifeline", "", styles.LIFELINE,
            center_x, lifeline_top,
            center_x, p.lifeline_end_y,
        )
        root.append(lifeline)

    # Edges (after all vertices)
    for edge in ir.edges:
        style = _resolve_edge_style(edge)

        if edge.source_x is not None:
            # Point-based edge (sequence diagrams)
            cell = build_point_edge_cell(
                edge.id, edge.label, style,
                edge.source_x, edge.source_y,
                edge.target_x, edge.target_y,
            )
        else:
            # Cell-ref edge (all other diagrams)
            cell = build_edge_cell(
                edge.id, edge.label, style,
                edge.source, edge.target,
            )
        root.append(cell)

    return tostring(root_elem, encoding="unicode")
