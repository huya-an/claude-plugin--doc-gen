"""End-to-end integration tests for the plugin pipeline."""

from mkdocs_drawio_plugin.converter import mermaid_to_figure, mermaid_to_html, mermaid_to_xml
from mkdocs_drawio_plugin.plugin import mermaid_fence_format


class TestEndToEndFlowchart:
    FLOWCHART = """graph TD
  Start[Start Process] --> Validate{Valid?}
  Validate -->|Yes| Process[Process Data]
  Validate -->|No| Error[Show Error]
  Process --> End[Done]
  Error --> End
"""

    def test_xml_has_all_nodes(self):
        xml = mermaid_to_xml(self.FLOWCHART)
        assert "Start Process" in xml
        assert "Valid?" in xml
        assert "Process Data" in xml
        assert "Show Error" in xml
        assert "Done" in xml

    def test_xml_has_edges(self):
        xml = mermaid_to_xml(self.FLOWCHART)
        assert 'edge="1"' in xml

    def test_html_is_valid_embed(self):
        html = mermaid_to_html(self.FLOWCHART)
        assert '<div class="mxgraph"' in html
        assert "data-mxgraph=" in html
        assert "&quot;" not in html
        assert "&lt;mxGraphModel&gt;" in html

    def test_figure_wrapping(self):
        html = mermaid_to_figure(self.FLOWCHART, "Process flow")
        assert '<figure class="drawio-diagram">' in html
        assert "<figcaption>Process flow</figcaption>" in html


class TestEndToEndSequence:
    SEQUENCE = """sequenceDiagram
  participant C as Client
  participant S as Server
  participant D as Database
  C->>S: POST /api/data
  S->>D: INSERT INTO records
  D-->>S: OK
  S-->>C: 200 OK
"""

    def test_xml_has_participants(self):
        xml = mermaid_to_xml(self.SEQUENCE)
        assert "Client" in xml
        assert "Server" in xml
        assert "Database" in xml

    def test_xml_uses_point_edges(self):
        """Sequence edges must use sourcePoint/targetPoint, not cell refs."""
        xml = mermaid_to_xml(self.SEQUENCE)
        assert "sourcePoint" in xml
        assert "targetPoint" in xml

    def test_xml_has_lifelines(self):
        xml = mermaid_to_xml(self.SEQUENCE)
        # Lifelines have endArrow=none style
        assert "endArrow=none" in xml

    def test_message_labels_preserved(self):
        xml = mermaid_to_xml(self.SEQUENCE)
        assert "POST /api/data" in xml
        assert "INSERT INTO records" in xml
        assert "200 OK" in xml


class TestEndToEndC4:
    C4 = """C4Context
  Person(user, "End User", "Uses the system")
  System(sys, "Main System", "Core platform")
  System_Ext(ext, "Payment Gateway", "Processes payments")
  Rel(user, sys, "Uses", "HTTPS")
  Rel(sys, ext, "Sends payments", "HTTPS/JSON")
"""

    def test_xml_has_elements(self):
        xml = mermaid_to_xml(self.C4)
        assert "End User" in xml
        assert "Main System" in xml
        assert "Payment Gateway" in xml

    def test_xml_has_relationships(self):
        xml = mermaid_to_xml(self.C4)
        assert 'edge="1"' in xml


class TestEndToEndErd:
    ERD = """erDiagram
  USER {
    int id PK
    string name
    string email UK
  }
  ORDER {
    int id PK
    int user_id FK
    float amount
  }
  USER ||--o{ ORDER : "places"
"""

    def test_xml_has_entities(self):
        xml = mermaid_to_xml(self.ERD)
        assert "USER" in xml
        assert "ORDER" in xml

    def test_xml_has_fields(self):
        xml = mermaid_to_xml(self.ERD)
        assert "id: int [PK]" in xml
        assert "name: string" in xml

    def test_xml_has_relationship(self):
        xml = mermaid_to_xml(self.ERD)
        assert 'edge="1"' in xml
        assert "places" in xml


class TestSuperFencesFormatter:
    def test_returns_figure_html(self):
        result = mermaid_fence_format(
            source="graph TD\n  A --> B",
            language="mermaid",
            css_class="mermaid",
            options={},
            md=None,
        )
        assert '<figure class="drawio-diagram">' in result

    def test_fallback_on_error(self):
        # Empty input should still produce something
        result = mermaid_fence_format(
            source="",
            language="mermaid",
            css_class="mermaid",
            options={},
            md=None,
        )
        # Should either produce a figure or a code block fallback
        assert "<" in result  # Some HTML output
