"""
Mermaid ERD (Entity Relationship Diagram) parser.

Handles `erDiagram` blocks with entities, attributes, and relationships.

Supported syntax:
  ENTITY {
      type field_name PK "comment"
      type field_name FK "comment"
      type field_name
  }
  ENTITY1 ||--o{ ENTITY2 : "relationship"
  ENTITY1 }o--|| ENTITY2 : "relationship"
"""

from __future__ import annotations

import re

from .base import (
    DiagramEdge,
    DiagramIR,
    DiagramNode,
    DiagramType,
    EdgeType,
    LayoutDirection,
    NodeShape,
)

_HEADER_RE = re.compile(r"^\s*erDiagram\s*$", re.IGNORECASE)

# Entity block start: ENTITY_NAME {
_ENTITY_START_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*$")

# Entity field: type name [PK|FK|UK] ["comment"]
_FIELD_RE = re.compile(
    r"^\s*(\S+)\s+(\S+)"          # type and name
    r"(?:\s+(PK|FK|SK|UK|GSI))?"  # optional constraint
    r'(?:\s+"([^"]*)")?'          # optional comment
    r"\s*$"
)

# Entity block end
_ENTITY_END_RE = re.compile(r"^\s*\}\s*$")

# Relationship line:
#   ENTITY1 ||--o{ ENTITY2 : "label"
#   ENTITY1 }|--|{ ENTITY2 : "label"
# Cardinality markers: ||, |{, o{, }|, }o, |o, o|
_RELATIONSHIP_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)"  # entity1
    r"\s+"
    r"([|o}]{1,2})"                   # left cardinality
    r"(--)"                            # separator
    r"([|o{]{1,2})"                   # right cardinality
    r"\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)"      # entity2
    r'\s*:\s*"?([^"]*)"?\s*$'         # label
)


def _cardinality_label(markers: str) -> str:
    """Convert Mermaid cardinality markers to ERD notation."""
    marker_map = {
        "||": "1",
        "|{": "*",
        "o{": "0..*",
        "}|": "*",
        "}o": "0..*",
        "|o": "0..1",
        "o|": "0..1",
        "o{": "0..*",
    }
    return marker_map.get(markers, markers)


def parse(text: str) -> DiagramIR:
    """Parse a Mermaid ERD into DiagramIR."""
    lines = text.strip().splitlines()
    if not lines:
        return DiagramIR(diagram_type=DiagramType.ERD)

    start_line = 0
    if _HEADER_RE.match(lines[0]):
        start_line = 1

    nodes: dict[str, DiagramNode] = {}
    edges: list[DiagramEdge] = []
    current_entity: str | None = None
    current_fields: list[str] = []
    edge_counter = 0

    for line in lines[start_line:]:
        stripped = line.strip()

        if not stripped or stripped.startswith("%%"):
            continue

        # Entity block start
        entity_match = _ENTITY_START_RE.match(stripped)
        if entity_match:
            current_entity = entity_match.group(1)
            current_fields = []
            continue

        # Entity block end
        if _ENTITY_END_RE.match(stripped) and current_entity:
            nodes[current_entity] = DiagramNode(
                id=current_entity,
                label=current_entity,
                shape=NodeShape.UML_CLASS,
                fields=current_fields,
                store_type="relational",  # default
            )
            current_entity = None
            current_fields = []
            continue

        # Field inside entity block
        if current_entity:
            field_match = _FIELD_RE.match(stripped)
            if field_match:
                ftype = field_match.group(1)
                fname = field_match.group(2)
                constraint = field_match.group(3) or ""
                comment = field_match.group(4) or ""

                badge = f" [{constraint}]" if constraint else ""
                desc = f"  {comment}" if comment else ""
                current_fields.append(f"{fname}: {ftype}{badge}{desc}")
            continue

        # Relationship
        rel_match = _RELATIONSHIP_RE.match(stripped)
        if rel_match:
            entity1 = rel_match.group(1)
            left_card = rel_match.group(2)
            right_card = rel_match.group(4)
            entity2 = rel_match.group(5)
            label = rel_match.group(6).strip()

            # Ensure entities exist even without field blocks
            if entity1 not in nodes:
                nodes[entity1] = DiagramNode(
                    id=entity1,
                    label=entity1,
                    shape=NodeShape.UML_CLASS,
                    store_type="relational",
                )
            if entity2 not in nodes:
                nodes[entity2] = DiagramNode(
                    id=entity2,
                    label=entity2,
                    shape=NodeShape.UML_CLASS,
                    store_type="relational",
                )

            left_label = _cardinality_label(left_card)
            right_label = _cardinality_label(right_card)
            full_label = f"{left_label}  {label}  {right_label}"

            edge_id = f"rel_{edge_counter}"
            edge_counter += 1
            edges.append(DiagramEdge(
                id=edge_id,
                source=entity1,
                target=entity2,
                label=full_label,
                edge_type=EdgeType.SYNC,
            ))
            continue

    return DiagramIR(
        diagram_type=DiagramType.ERD,
        layout=LayoutDirection.LR,
        nodes=list(nodes.values()),
        edges=edges,
    )
