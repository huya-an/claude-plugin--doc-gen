"""Tests for the encoding module."""

from mkdocs_drawio_plugin.encoding import (
    encode_for_mxgraph,
    html_entity_encode,
    json_escape,
    wrap_in_mxgraph_div,
    xml_to_html,
)


class TestJsonEscape:
    def test_escapes_double_quotes(self):
        assert json_escape('id="0"') == 'id=\\"0\\"'

    def test_escapes_backslashes(self):
        assert json_escape("a\\b") == "a\\\\b"

    def test_escapes_both(self):
        assert json_escape('a\\"b') == 'a\\\\\\"b'

    def test_no_change_for_clean_string(self):
        assert json_escape("hello world") == "hello world"


class TestHtmlEntityEncode:
    def test_encodes_ampersand(self):
        assert html_entity_encode("a&b") == "a&amp;b"

    def test_encodes_less_than(self):
        assert html_entity_encode("<tag>") == "&lt;tag&gt;"

    def test_encodes_greater_than(self):
        assert html_entity_encode("a>b") == "a&gt;b"

    def test_ampersand_encoded_first(self):
        # & in <mxCell must become &amp;lt; not &lt;
        result = html_entity_encode("&lt;")
        assert result == "&amp;lt;"

    def test_no_change_for_clean_string(self):
        assert html_entity_encode("hello") == "hello"


class TestEncodeForMxgraph:
    def test_full_pipeline(self):
        xml = '<mxCell id="0"/>'
        result = encode_for_mxgraph(xml)
        # Step 1: " -> \"  => <mxCell id=\"0\"/>
        # Step 2: < -> &lt;, > -> &gt;  => &lt;mxCell id=\"0\"/&gt;
        assert result == '&lt;mxCell id=\\"0\\"/ &gt;'.replace("/ ", "/")  # keep space in "mxCell id"

    def test_no_quot_entities(self):
        """CRITICAL: &quot; must NEVER appear in output."""
        xml = '<mxCell id="0" style="rounded=1;"/>'
        result = encode_for_mxgraph(xml)
        assert "&quot;" not in result

    def test_preserves_content(self):
        xml = '<mxCell id="2" value="Hello World" vertex="1" parent="1"/>'
        result = encode_for_mxgraph(xml)
        assert "&quot;" not in result
        assert '\\"' in result  # JSON-escaped quotes preserved after HTML encoding


class TestWrapInMxgraphDiv:
    def test_produces_valid_div(self):
        result = wrap_in_mxgraph_div("encoded_xml_here")
        assert result.startswith('<div class="mxgraph"')
        assert "data-mxgraph='" in result
        assert result.endswith("'></div>")
        assert '"xml":"encoded_xml_here"' in result

    def test_contains_viewer_options(self):
        result = wrap_in_mxgraph_div("test")
        assert '"nav":true' in result
        assert '"resize":true' in result
        assert '"fit":true' in result
        assert '"toolbar":"zoom layers lightbox"' in result


class TestXmlToHtml:
    def test_end_to_end(self):
        xml = '<mxGraphModel><root><mxCell id="0"/></root></mxGraphModel>'
        result = xml_to_html(xml)
        assert '<div class="mxgraph"' in result
        assert "&quot;" not in result
        assert "&lt;mxGraphModel&gt;" in result
