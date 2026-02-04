"""Tests for the flowchart parser."""

from mkdocs_drawio_plugin.parsers.flowchart import parse
from mkdocs_drawio_plugin.parsers.base import (
    DiagramType,
    EdgeType,
    LayoutDirection,
    NodeShape,
)


class TestFlowchartParser:
    def test_basic_td(self):
        ir = parse("graph TD\n  A --> B")
        assert ir.diagram_type == DiagramType.FLOWCHART
        assert ir.layout == LayoutDirection.TB

    def test_basic_lr(self):
        ir = parse("graph LR\n  A --> B")
        assert ir.layout == LayoutDirection.LR

    def test_node_shapes(self):
        text = """graph TD
  A[Rectangle]
  B(Rounded)
  C{Diamond}
  D[(Cylinder)]
  E((Circle))
"""
        ir = parse(text)
        nodes = {n.id: n for n in ir.nodes}
        assert nodes["A"].shape == NodeShape.RECT
        assert nodes["A"].label == "Rectangle"
        assert nodes["B"].shape == NodeShape.ROUNDED_RECT
        assert nodes["C"].shape == NodeShape.DIAMOND
        assert nodes["D"].shape == NodeShape.CYLINDER
        assert nodes["E"].shape == NodeShape.CIRCLE

    def test_edges_created(self):
        ir = parse("graph TD\n  A --> B\n  B --> C")
        assert len(ir.edges) >= 2
        sources = {e.source for e in ir.edges}
        targets = {e.target for e in ir.edges}
        assert "A" in sources
        assert "B" in sources
        assert "B" in targets
        assert "C" in targets

    def test_dotted_edge(self):
        ir = parse("graph TD\n  A -.-> B")
        assert len(ir.edges) >= 1
        assert ir.edges[0].edge_type == EdgeType.ASYNC

    def test_thick_edge(self):
        ir = parse("graph TD\n  A ==> B")
        assert len(ir.edges) >= 1
        assert ir.edges[0].edge_type == EdgeType.DATA_FLOW

    def test_labeled_edge_pipe_style(self):
        ir = parse("graph TD\n  A -->|Yes| B")
        assert len(ir.edges) >= 1
        assert ir.edges[0].label == "Yes"

    def test_subgraph(self):
        text = """graph TD
  subgraph Backend
    A[API] --> B[DB]
  end
"""
        ir = parse(text)
        assert len(ir.groups) == 1
        assert ir.groups[0].label == "Backend"

    def test_implicit_node_creation(self):
        """Nodes referenced in edges but not declared should be created."""
        ir = parse("graph TD\n  X --> Y")
        node_ids = {n.id for n in ir.nodes}
        assert "X" in node_ids
        assert "Y" in node_ids

    def test_comment_lines_skipped(self):
        ir = parse("graph TD\n  %% comment\n  A --> B")
        assert len(ir.nodes) >= 2

    def test_empty_input(self):
        ir = parse("")
        assert ir.diagram_type == DiagramType.FLOWCHART
        assert len(ir.nodes) == 0
