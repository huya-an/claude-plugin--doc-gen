"""Tests for the ERD parser."""

from mkdocs_drawio_plugin.parsers.erd import parse
from mkdocs_drawio_plugin.parsers.base import DiagramType, LayoutDirection, NodeShape


class TestErdParser:
    def test_basic_erd(self):
        text = """erDiagram
  USER {
    int id PK
    string name
    string email UK
  }
  ORDER {
    int id PK
    int user_id FK
    float total
  }
  USER ||--o{ ORDER : "places"
"""
        ir = parse(text)
        assert ir.diagram_type == DiagramType.ERD
        assert ir.layout == LayoutDirection.LR
        assert len(ir.nodes) == 2
        assert len(ir.edges) == 1

    def test_entity_fields(self):
        text = """erDiagram
  USER {
    int id PK
    string name
    string email UK "unique email"
  }
"""
        ir = parse(text)
        user = ir.nodes[0]
        assert user.shape == NodeShape.UML_CLASS
        assert len(user.fields) == 3
        assert "id: int [PK]" in user.fields[0]
        assert "name: string" in user.fields[1]
        assert "[UK]" in user.fields[2]
        assert "unique email" in user.fields[2]

    def test_relationship_entities_created(self):
        """Entities referenced in relationships but not declared get created."""
        text = """erDiagram
  A ||--o{ B : "has"
"""
        ir = parse(text)
        assert len(ir.nodes) == 2
        assert ir.nodes[0].id == "A"
        assert ir.nodes[1].id == "B"

    def test_multiple_relationships(self):
        text = """erDiagram
  A ||--o{ B : "has"
  B ||--|{ C : "contains"
"""
        ir = parse(text)
        assert len(ir.edges) == 2

    def test_relationship_labels(self):
        text = """erDiagram
  USER ||--o{ ORDER : "places"
"""
        ir = parse(text)
        edge = ir.edges[0]
        assert "places" in edge.label

    def test_empty_input(self):
        ir = parse("")
        assert ir.diagram_type == DiagramType.ERD
        assert len(ir.nodes) == 0
