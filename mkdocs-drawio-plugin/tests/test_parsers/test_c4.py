"""Tests for the C4 diagram parser."""

from mkdocs_drawio_plugin.parsers.c4 import parse
from mkdocs_drawio_plugin.parsers.base import DiagramType, NodeShape


class TestC4Parser:
    def test_c4_context(self):
        text = """C4Context
  Person(user, "User", "A user of the system")
  System(sys, "System", "The main system")
  Rel(user, sys, "Uses")
"""
        ir = parse(text)
        assert ir.diagram_type == DiagramType.C4_CONTEXT
        assert len(ir.nodes) == 2
        assert len(ir.edges) == 1

    def test_person_shape(self):
        text = """C4Context
  Person(u, "User", "desc")
"""
        ir = parse(text)
        assert ir.nodes[0].shape == NodeShape.PERSON
        assert ir.nodes[0].semantic_role == "person"

    def test_external_system(self):
        text = """C4Context
  System_Ext(ext, "External API", "Third party")
"""
        ir = parse(text)
        assert ir.nodes[0].semantic_role == "external"

    def test_c4_container(self):
        text = """C4Container
  Container(api, "API", "Python", "REST API")
  ContainerDb(db, "Database", "PostgreSQL", "Stores data")
  Rel(api, db, "Reads/Writes", "SQL")
"""
        ir = parse(text)
        assert ir.diagram_type == DiagramType.C4_CONTAINER
        assert len(ir.nodes) == 2
        assert ir.nodes[1].shape == NodeShape.CYLINDER

    def test_c4_component(self):
        text = """C4Component
  Component(handler, "RequestHandler", "Python", "Handles requests")
  Component(validator, "Validator", "Python", "Validates input")
  Rel(handler, validator, "Calls")
"""
        ir = parse(text)
        assert ir.diagram_type == DiagramType.C4_COMPONENT

    def test_boundary(self):
        text = """C4Container
  System_Boundary(sb, "My System") {
    Container(api, "API", "Python")
    ContainerDb(db, "DB", "Postgres")
  }
  Rel(api, db, "Uses")
"""
        ir = parse(text)
        assert len(ir.groups) == 1
        assert ir.groups[0].label == "My System"
        # Nodes inside boundary should have parent_group set
        api_node = ir.node_by_id("api")
        assert api_node is not None
        assert api_node.parent_group is not None

    def test_relationship_label_with_technology(self):
        text = """C4Context
  System(a, "A")
  System(b, "B")
  Rel(a, b, "Sends data", "HTTPS/JSON")
"""
        ir = parse(text)
        assert "[HTTPS/JSON]" in ir.edges[0].label

    def test_multiline_label(self):
        text = """C4Context
  Person(u, "Admin User", "System administrator")
"""
        ir = parse(text)
        # Label should contain bold name and description
        assert "<b>Admin User</b>" in ir.nodes[0].label
        assert "System administrator" in ir.nodes[0].label

    def test_quoted_args(self):
        text = """C4Context
  System(sys, "My System, v2", "Description with, comma")
"""
        ir = parse(text)
        assert ir.nodes[0].id == "sys"
        assert "My System, v2" in ir.nodes[0].label

    def test_empty_input(self):
        ir = parse("")
        assert ir.diagram_type == DiagramType.C4_CONTEXT
