"""
Intermediate Representation (IR) for parsed Mermaid diagrams.

All parsers produce a DiagramIR that generators consume. This decouples
parsing from XML generation — any parser can feed any generator as long
as the IR contract is satisfied.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DiagramType(Enum):
    """Supported diagram types."""

    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    C4_CONTEXT = "c4-context"
    C4_CONTAINER = "c4-container"
    C4_COMPONENT = "c4-component"
    C4_CODE = "c4-code"
    ERD = "erd"
    GENERIC = "generic"


class NodeShape(Enum):
    """Node shape variants."""

    RECT = "rect"  # [label]
    ROUNDED_RECT = "rounded_rect"  # (label)
    STADIUM = "stadium"  # ([label])
    CYLINDER = "cylinder"  # [(label)]
    CIRCLE = "circle"  # ((label))
    DIAMOND = "diamond"  # {label}
    HEXAGON = "hexagon"  # {{label}}
    PARALLELOGRAM = "parallelogram"  # [/label/]
    PERSON = "person"
    UML_CLASS = "uml_class"
    START_END = "start_end"
    ERROR_END = "error_end"


class EdgeType(Enum):
    """Edge interaction types."""

    SYNC = "sync"
    ASYNC = "async"
    ERROR = "error"
    ERROR_RESPONSE = "error_response"
    RETRY = "retry"
    ROLLBACK = "rollback"
    DATA_FLOW = "data_flow"
    DEPENDENCY = "dependency"
    NUMBERED = "numbered"
    # Sequence-specific
    SEQ_REQUEST = "seq_request"
    SEQ_RESPONSE = "seq_response"
    SEQ_ERROR = "seq_error"


class LayoutDirection(Enum):
    """Diagram layout direction."""

    TB = "TB"  # top-to-bottom
    LR = "LR"  # left-to-right


@dataclass
class DiagramNode:
    """A node in the diagram IR."""

    id: str
    label: str
    shape: NodeShape = NodeShape.ROUNDED_RECT
    semantic_role: Optional[str] = None  # maps to styles.NODE_STYLES key
    x: float = 0.0
    y: float = 0.0
    width: float = 160.0
    height: float = 80.0
    parent_group: Optional[str] = None
    # For UML class boxes / ERD entities
    fields: list[str] = field(default_factory=list)
    # Arbitrary style override (if set, overrides semantic_role lookup)
    style_override: Optional[str] = None
    # Sub-type for ERD entities
    store_type: Optional[str] = None  # relational, nosql, cache, search


@dataclass
class DiagramEdge:
    """An edge in the diagram IR."""

    id: str
    source: str  # source node ID
    target: str  # target node ID
    label: str = ""
    edge_type: EdgeType = EdgeType.SYNC
    # For sequence diagrams: explicit coordinates instead of cell refs
    source_x: Optional[float] = None
    source_y: Optional[float] = None
    target_x: Optional[float] = None
    target_y: Optional[float] = None
    # Arbitrary style override
    style_override: Optional[str] = None


@dataclass
class DiagramGroup:
    """A group/section containing child nodes."""

    id: str
    label: str
    group_type: str = "success"  # maps to styles.GROUP_STYLES key
    x: float = 0.0
    y: float = 0.0
    width: float = 600.0
    height: float = 200.0
    # For UML class/swimlane style groups
    style_override: Optional[str] = None


@dataclass
class SequenceParticipant:
    """A participant in a sequence diagram."""

    id: str
    label: str
    semantic_role: Optional[str] = None
    x: float = 0.0
    y: float = 30.0
    width: float = 140.0
    height: float = 50.0
    lifeline_end_y: float = 300.0


@dataclass
class DiagramIR:
    """Complete intermediate representation of a parsed diagram."""

    diagram_type: DiagramType
    title: str = ""
    layout: LayoutDirection = LayoutDirection.TB
    nodes: list[DiagramNode] = field(default_factory=list)
    edges: list[DiagramEdge] = field(default_factory=list)
    groups: list[DiagramGroup] = field(default_factory=list)
    # Sequence diagram specific
    participants: list[SequenceParticipant] = field(default_factory=list)

    def node_by_id(self, node_id: str) -> Optional[DiagramNode]:
        """Look up a node by its ID."""
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def validate(self) -> list[str]:
        """Check IR invariants. Returns list of warning messages."""
        warnings = []
        node_ids = {n.id for n in self.nodes}
        participant_ids = {p.id for p in self.participants}
        all_ids = node_ids | participant_ids

        if self.nodes and not self.edges:
            if len(self.nodes) > 1:
                warnings.append(
                    f"Diagram has {len(self.nodes)} nodes but 0 edges — "
                    "every multi-node diagram must have edges."
                )

        for edge in self.edges:
            # Sequence edges use coordinates, not node refs
            if edge.source_x is not None:
                continue
            if edge.source not in all_ids:
                warnings.append(
                    f"Edge {edge.id} references unknown source '{edge.source}'"
                )
            if edge.target not in all_ids:
                warnings.append(
                    f"Edge {edge.id} references unknown target '{edge.target}'"
                )

        return warnings
