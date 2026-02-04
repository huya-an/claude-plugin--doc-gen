"""
Mermaid sequence diagram parser.

Handles `sequenceDiagram` blocks with participants, messages, notes,
alt/opt/loop/par blocks, and activations.

CRITICAL: Messages use explicit sourcePoint/targetPoint coordinates,
NOT cell ID references (per drawio-patterns.md sequence diagram rules).
"""

from __future__ import annotations

import re

from .base import (
    DiagramEdge,
    DiagramGroup,
    DiagramIR,
    DiagramType,
    EdgeType,
    LayoutDirection,
    SequenceParticipant,
)

# Header
_HEADER_RE = re.compile(r"^\s*sequenceDiagram\s*$", re.IGNORECASE)

# Participant declarations
_PARTICIPANT_RE = re.compile(
    r"^\s*(?:participant|actor)\s+(\S+?)(?:\s+as\s+(.+))?\s*$", re.IGNORECASE
)

# Message arrows (Mermaid syntax):
#   A->>B: label    solid arrow
#   A-->>B: label   dashed arrow (response)
#   A-xB: label     cross (error/lost)
#   A--xB: label    dashed cross
#   A-)B: label     async
#   A--)B: label    dashed async
_MESSAGE_RE = re.compile(
    r"^\s*(\S+?)\s*"
    r"(->>|-->>|-x|--x|-\)|--\))"
    r"\s*(\S+?)\s*:\s*(.+)$"
)

# Blocks: alt, else, opt, loop, par, and, rect, note, end
_BLOCK_START_RE = re.compile(
    r"^\s*(alt|opt|loop|par|rect|critical)\s+(.*)$", re.IGNORECASE
)
_BLOCK_ELSE_RE = re.compile(r"^\s*(else|and)\s*(.*)$", re.IGNORECASE)
_BLOCK_END_RE = re.compile(r"^\s*end\s*$", re.IGNORECASE)

# Note
_NOTE_RE = re.compile(
    r"^\s*note\s+(left of|right of|over)\s+(\S+?)(?:,\s*(\S+?))?\s*:\s*(.+)$",
    re.IGNORECASE,
)

# Activation
_ACTIVATE_RE = re.compile(r"^\s*activate\s+(\S+)\s*$", re.IGNORECASE)
_DEACTIVATE_RE = re.compile(r"^\s*deactivate\s+(\S+)\s*$", re.IGNORECASE)

# Semantic role hints from participant names
_ROLE_HINTS = {
    "client": "queue",       # orange
    "browser": "queue",
    "user": "person",
    "server": "compute",     # blue
    "api": "networking",     # purple
    "gateway": "networking",
    "db": "database",        # green
    "database": "database",
    "cache": "database",
    "redis": "database",
    "queue": "queue",        # orange
    "sqs": "queue",
    "kafka": "queue",
    "auth": "security",      # red
    "cognito": "security",
}


def _guess_role(name: str) -> str | None:
    """Guess semantic role from participant name."""
    lower = name.lower()
    for hint, role in _ROLE_HINTS.items():
        if hint in lower:
            return role
    return "compute"  # default blue


def _classify_arrow(arrow: str) -> EdgeType:
    """Map Mermaid arrow syntax to EdgeType."""
    if arrow in ("-x", "--x"):
        return EdgeType.SEQ_ERROR
    if arrow.startswith("--"):
        return EdgeType.SEQ_RESPONSE
    return EdgeType.SEQ_REQUEST


def parse(text: str) -> DiagramIR:
    """Parse a Mermaid sequence diagram into DiagramIR."""
    lines = text.strip().splitlines()
    if not lines:
        return DiagramIR(diagram_type=DiagramType.SEQUENCE)

    participants: dict[str, SequenceParticipant] = {}
    participant_order: list[str] = []
    edges: list[DiagramEdge] = []
    groups: list[DiagramGroup] = []
    edge_counter = 0
    group_stack: list[str] = []
    group_counter = 0

    start_line = 0
    if _HEADER_RE.match(lines[0]):
        start_line = 1

    def _ensure_participant(pid: str, display: str | None = None) -> None:
        if pid not in participants:
            participants[pid] = SequenceParticipant(
                id=pid,
                label=display or pid,
                semantic_role=_guess_role(pid),
            )
            participant_order.append(pid)
        elif display:
            participants[pid].label = display

    for line in lines[start_line:]:
        stripped = line.strip()

        if not stripped or stripped.startswith("%%"):
            continue

        # Participant declaration
        p_match = _PARTICIPANT_RE.match(stripped)
        if p_match:
            pid = p_match.group(1)
            display = p_match.group(2) or pid
            _ensure_participant(pid, display)
            continue

        # Message
        msg_match = _MESSAGE_RE.match(stripped)
        if msg_match:
            src = msg_match.group(1)
            arrow = msg_match.group(2)
            tgt = msg_match.group(3)
            label = msg_match.group(4).strip()

            _ensure_participant(src)
            _ensure_participant(tgt)

            edge_type = _classify_arrow(arrow)
            edge_id = f"msg_{edge_counter}"
            edge_counter += 1

            # Coordinates will be set by layout_sequence()
            # For now, store source/target as participant IDs
            edges.append(DiagramEdge(
                id=edge_id,
                source=src,
                target=tgt,
                label=label,
                edge_type=edge_type,
            ))
            continue

        # Block start (alt, opt, loop, par, critical)
        block_match = _BLOCK_START_RE.match(stripped)
        if block_match:
            block_type = block_match.group(1).lower()
            block_label = block_match.group(2).strip()
            group_counter += 1
            gid = f"block_{group_counter}"

            # Map block type to group style
            type_map = {
                "alt": "warning",
                "opt": "info",
                "loop": "warning",
                "par": "info",
                "critical": "danger",
                "rect": "success",
            }
            groups.append(DiagramGroup(
                id=gid,
                label=f"{block_type.upper()}: {block_label}",
                group_type=type_map.get(block_type, "info"),
            ))
            group_stack.append(gid)
            continue

        # Block else/and
        if _BLOCK_ELSE_RE.match(stripped):
            # For simplicity, treat else as a new group
            group_counter += 1
            gid = f"block_{group_counter}"
            match = _BLOCK_ELSE_RE.match(stripped)
            label = match.group(2).strip() if match.group(2) else "else"
            groups.append(DiagramGroup(
                id=gid,
                label=label,
                group_type="warning",
            ))
            if group_stack:
                group_stack[-1] = gid
            continue

        # Block end
        if _BLOCK_END_RE.match(stripped):
            if group_stack:
                group_stack.pop()
            continue

        # Note (skip for now — could add as text labels later)
        if _NOTE_RE.match(stripped):
            continue

        # Activate/deactivate (skip for now)
        if _ACTIVATE_RE.match(stripped) or _DEACTIVATE_RE.match(stripped):
            continue

    return DiagramIR(
        diagram_type=DiagramType.SEQUENCE,
        layout=LayoutDirection.TB,
        participants=list(participants.values()),
        edges=edges,
        groups=groups,
    )
