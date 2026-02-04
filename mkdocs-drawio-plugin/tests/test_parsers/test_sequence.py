"""Tests for the sequence diagram parser."""

from mkdocs_drawio_plugin.parsers.sequence import parse
from mkdocs_drawio_plugin.parsers.base import DiagramType, EdgeType


class TestSequenceParser:
    def test_basic_sequence(self):
        text = """sequenceDiagram
  Alice->>Bob: Hello
  Bob-->>Alice: Hi back
"""
        ir = parse(text)
        assert ir.diagram_type == DiagramType.SEQUENCE
        assert len(ir.participants) == 2
        assert len(ir.edges) == 2

    def test_participant_order(self):
        text = """sequenceDiagram
  participant A as Alice
  participant B as Bob
  A->>B: msg
"""
        ir = parse(text)
        assert ir.participants[0].id == "A"
        assert ir.participants[0].label == "Alice"
        assert ir.participants[1].id == "B"
        assert ir.participants[1].label == "Bob"

    def test_message_types(self):
        text = """sequenceDiagram
  A->>B: request
  B-->>A: response
  A-xB: error
"""
        ir = parse(text)
        assert ir.edges[0].edge_type == EdgeType.SEQ_REQUEST
        assert ir.edges[1].edge_type == EdgeType.SEQ_RESPONSE
        assert ir.edges[2].edge_type == EdgeType.SEQ_ERROR

    def test_message_labels_preserved(self):
        text = """sequenceDiagram
  Client->>Server: POST /api/users
  Server-->>Client: 201 Created
"""
        ir = parse(text)
        assert ir.edges[0].label == "POST /api/users"
        assert ir.edges[1].label == "201 Created"

    def test_implicit_participants(self):
        """Participants referenced in messages but not declared are created."""
        text = """sequenceDiagram
  X->>Y: hello
"""
        ir = parse(text)
        assert len(ir.participants) == 2
        p_ids = {p.id for p in ir.participants}
        assert "X" in p_ids
        assert "Y" in p_ids

    def test_alt_block(self):
        text = """sequenceDiagram
  A->>B: request
  alt success
    B-->>A: 200 OK
  else error
    B-->>A: 500 Error
  end
"""
        ir = parse(text)
        assert len(ir.groups) >= 1
        assert len(ir.edges) == 3

    def test_loop_block(self):
        text = """sequenceDiagram
  A->>B: poll
  loop Every 5s
    B-->>A: status
  end
"""
        ir = parse(text)
        assert len(ir.groups) >= 1
        assert any("LOOP" in g.label for g in ir.groups)

    def test_semantic_role_guessing(self):
        text = """sequenceDiagram
  Client->>Server: request
  Server->>Database: query
"""
        ir = parse(text)
        roles = {p.id: p.semantic_role for p in ir.participants}
        assert roles["Client"] == "queue"  # orange
        assert roles["Server"] == "compute"  # blue
        assert roles["Database"] == "database"  # green

    def test_empty_input(self):
        ir = parse("")
        assert ir.diagram_type == DiagramType.SEQUENCE
        assert len(ir.participants) == 0
