"""Tests for the base XML generator."""

from mkdocs_drawio_plugin.generators.base import (
    build_edge_cell,
    build_point_edge_cell,
    build_vertex_cell,
    ir_to_xml,
)
from mkdocs_drawio_plugin.parsers.base import (
    DiagramEdge,
    DiagramIR,
    DiagramNode,
    DiagramType,
    EdgeType,
    SequenceParticipant,
)


class TestBuildVertexCell:
    def test_creates_cell_element(self):
        from xml.etree.ElementTree import tostring

        cell = build_vertex_cell("2", "Hello", "rounded=1;", 10, 20, 160, 80)
        xml = tostring(cell, encoding="unicode")
        assert 'id="2"' in xml
        assert 'value="Hello"' in xml
        assert 'vertex="1"' in xml
        assert 'x="10"' in xml
        assert 'width="160"' in xml


class TestBuildEdgeCell:
    def test_creates_edge_element(self):
        from xml.etree.ElementTree import tostring

        cell = build_edge_cell("e1", "calls", "endArrow=blockThin;", "2", "3")
        xml = tostring(cell, encoding="unicode")
        assert 'edge="1"' in xml
        assert 'source="2"' in xml
        assert 'target="3"' in xml


class TestBuildPointEdgeCell:
    def test_creates_point_based_edge(self):
        from xml.etree.ElementTree import tostring

        cell = build_point_edge_cell(
            "e1", "msg", "endArrow=blockThin;",
            100, 120, 300, 120,
        )
        xml = tostring(cell, encoding="unicode")
        assert 'edge="1"' in xml
        assert "sourcePoint" in xml
        assert "targetPoint" in xml
        assert 'x="100"' in xml
        assert 'x="300"' in xml


class TestIrToXml:
    def test_basic_diagram(self):
        ir = DiagramIR(
            diagram_type=DiagramType.FLOWCHART,
            nodes=[
                DiagramNode(id="2", label="A", x=50, y=50),
                DiagramNode(id="3", label="B", x=50, y=170),
            ],
            edges=[
                DiagramEdge(id="e1", source="2", target="3", label="next"),
            ],
        )
        xml = ir_to_xml(ir)
        assert "<mxGraphModel>" in xml
        assert 'id="0"' in xml
        assert 'id="1"' in xml
        assert 'id="2"' in xml
        assert 'id="3"' in xml
        assert 'id="e1"' in xml

    def test_sequence_diagram(self):
        ir = DiagramIR(
            diagram_type=DiagramType.SEQUENCE,
            participants=[
                SequenceParticipant(
                    id="p1", label="Alice", x=50, y=30,
                    width=140, height=50, lifeline_end_y=300,
                ),
            ],
            edges=[
                DiagramEdge(
                    id="m1", source="p1", target="p2",
                    label="hello", edge_type=EdgeType.SEQ_REQUEST,
                    source_x=120, source_y=120,
                    target_x=320, target_y=120,
                ),
            ],
        )
        xml = ir_to_xml(ir)
        assert "Alice" in xml
        assert "sourcePoint" in xml
        assert "hello" in xml

    def test_no_edges_warning(self):
        ir = DiagramIR(
            diagram_type=DiagramType.FLOWCHART,
            nodes=[
                DiagramNode(id="2", label="A"),
                DiagramNode(id="3", label="B"),
            ],
        )
        warnings = ir.validate()
        assert any("0 edges" in w for w in warnings)
