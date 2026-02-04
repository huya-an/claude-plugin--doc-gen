"""
ERD generator — converts ERD DiagramIR to draw.io XML with UML class boxes.

ERD entities use swimlane-style cells with a header row and field rows.
Each field is a child cell inside the swimlane.
"""

from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from ..parsers.base import DiagramIR, DiagramNode
from ..layout import auto_layout
from .. import styles
from .base import build_edge_cell, _resolve_edge_style


def _build_entity_cells(
    node: DiagramNode, root: Element,
) -> None:
    """Build swimlane header + field rows for an ERD entity."""
    # Determine header style by store type
    header_style = styles.ERD_STYLES.get(
        node.store_type or "relational", styles.ERD_RELATIONAL
    )

    total_height = styles.ERD_ENTITY_HEADER_HEIGHT + (
        len(node.fields) * styles.ERD_FIELD_HEIGHT
    )
    if not node.fields:
        total_height = styles.ERD_ENTITY_HEADER_HEIGHT + 40  # minimum body

    # Swimlane container
    cell = Element("mxCell")
    cell.set("id", node.id)
    cell.set("value", node.label)
    cell.set("style", header_style)
    cell.set("vertex", "1")
    cell.set("parent", node.parent_group or "1")

    geo = SubElement(cell, "mxGeometry")
    geo.set("x", str(node.x))
    geo.set("y", str(node.y))
    geo.set("width", str(node.width))
    geo.set("height", str(total_height))
    geo.set("as", "geometry")
    root.append(cell)

    # Field rows as child cells
    for i, field_text in enumerate(node.fields):
        field_cell = Element("mxCell")
        field_cell.set("id", f"{node.id}_f{i}")
        field_cell.set("value", field_text)
        field_cell.set("style", styles.ERD_FIELD)
        field_cell.set("vertex", "1")
        field_cell.set("parent", node.id)  # child of swimlane

        field_geo = SubElement(field_cell, "mxGeometry")
        field_geo.set("y", str(styles.ERD_ENTITY_HEADER_HEIGHT + i * styles.ERD_FIELD_HEIGHT))
        field_geo.set("width", str(node.width))
        field_geo.set("height", str(styles.ERD_FIELD_HEIGHT))
        field_geo.set("as", "geometry")
        root.append(field_cell)


def generate(ir: DiagramIR) -> str:
    """Generate draw.io XML from an ERD DiagramIR."""
    # Set entity dimensions based on field count
    for node in ir.nodes:
        node.width = styles.ERD_ENTITY_WIDTH
        field_height = len(node.fields) * styles.ERD_FIELD_HEIGHT
        node.height = styles.ERD_ENTITY_HEADER_HEIGHT + max(field_height, 40)

    auto_layout(ir)

    # Build XML
    root_elem = Element("mxGraphModel")
    root = SubElement(root_elem, "root")

    cell0 = SubElement(root, "mxCell")
    cell0.set("id", "0")
    cell1 = SubElement(root, "mxCell")
    cell1.set("id", "1")
    cell1.set("parent", "0")

    # Entities
    for node in ir.nodes:
        _build_entity_cells(node, root)

    # Edges
    for edge in ir.edges:
        style = _resolve_edge_style(edge)
        cell = build_edge_cell(
            edge.id, edge.label, style,
            edge.source, edge.target,
        )
        root.append(cell)

    return tostring(root_elem, encoding="unicode")
