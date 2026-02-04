"""Tests for the converter orchestrator."""

from mkdocs_drawio_plugin.converter import (
    detect_type,
    mermaid_to_figure,
    mermaid_to_html,
    mermaid_to_ir,
    mermaid_to_xml,
)
from mkdocs_drawio_plugin.parsers.base import DiagramType


class TestDetectType:
    def test_flowchart_graph_td(self):
        assert detect_type("graph TD\n  A --> B") == DiagramType.FLOWCHART

    def test_flowchart_lr(self):
        assert detect_type("flowchart LR\n  A --> B") == DiagramType.FLOWCHART

    def test_sequence(self):
        assert detect_type("sequenceDiagram\n  A->>B: msg") == DiagramType.SEQUENCE

    def test_c4_context(self):
        assert detect_type("C4Context\n  Person(a, b)") == DiagramType.C4_CONTEXT

    def test_c4_container(self):
        assert detect_type("C4Container\n  Container(a, b)") == DiagramType.C4_CONTAINER

    def test_erd(self):
        assert detect_type("erDiagram\n  A ||--o{ B : has") == DiagramType.ERD

    def test_unknown_falls_to_generic(self):
        assert detect_type("pie\n  data") == DiagramType.GENERIC

    def test_comment_lines_skipped(self):
        assert detect_type("%% comment\ngraph TD\n  A --> B") == DiagramType.FLOWCHART


class TestMermaidToXml:
    def test_flowchart_produces_xml(self):
        text = "graph TD\n  A[Start] --> B[End]"
        xml = mermaid_to_xml(text)
        assert "<mxGraphModel>" in xml
        assert "Start" in xml
        assert "End" in xml

    def test_sequence_produces_xml(self):
        text = "sequenceDiagram\n  Alice->>Bob: Hello\n  Bob-->>Alice: Hi"
        xml = mermaid_to_xml(text)
        assert "<mxGraphModel>" in xml
        assert "Hello" in xml
        assert "Hi" in xml

    def test_erd_produces_xml(self):
        text = 'erDiagram\n  USER ||--o{ ORDER : places'
        xml = mermaid_to_xml(text)
        assert "<mxGraphModel>" in xml
        assert "USER" in xml
        assert "ORDER" in xml


class TestMermaidToHtml:
    def test_produces_div(self):
        text = "graph TD\n  A --> B"
        html = mermaid_to_html(text)
        assert '<div class="mxgraph"' in html
        assert "data-mxgraph=" in html
        assert "&quot;" not in html  # CRITICAL: no &quot;

    def test_no_raw_xml_in_output(self):
        text = "graph TD\n  A --> B"
        html = mermaid_to_html(text)
        assert "<mxGraphModel>" not in html  # Should be encoded
        assert "&lt;mxGraphModel&gt;" in html


class TestMermaidToFigure:
    def test_wraps_in_figure(self):
        text = "graph TD\n  A --> B"
        html = mermaid_to_figure(text, caption="Test diagram")
        assert '<figure class="drawio-diagram">' in html
        assert "<figcaption>Test diagram</figcaption>" in html
        assert "</figure>" in html

    def test_no_caption(self):
        text = "graph TD\n  A --> B"
        html = mermaid_to_figure(text)
        assert "<figcaption>" not in html


class TestMermaidToIr:
    def test_flowchart_ir_has_nodes_and_edges(self):
        text = "graph TD\n  A[Start] --> B[End]"
        ir = mermaid_to_ir(text)
        assert ir.diagram_type == DiagramType.FLOWCHART
        assert len(ir.nodes) >= 2
        assert len(ir.edges) >= 1

    def test_sequence_ir_has_participants(self):
        text = "sequenceDiagram\n  Alice->>Bob: Hello"
        ir = mermaid_to_ir(text)
        assert ir.diagram_type == DiagramType.SEQUENCE
        assert len(ir.participants) == 2
        assert len(ir.edges) == 1
