"""
Draw.io style constants transcribed from drawio-patterns.md.

All style strings, colors, and geometry defaults live here so parsers
and generators reference a single source of truth.
"""

# ---------------------------------------------------------------------------
# Node styles — by semantic role
# ---------------------------------------------------------------------------

NODE_COMPUTE = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#438DD5;fontColor=#ffffff;strokeColor=#3C7FC0;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

NODE_QUEUE = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E8A735;fontColor=#ffffff;strokeColor=#C88B1E;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

NODE_DATABASE = (
    "shape=cylinder3;whiteSpace=wrap;html=1;"
    "fillColor=#4CAF50;fontColor=#ffffff;strokeColor=#388E3C;"
    "boundedLbl=1;backgroundOutline=1;size=12;fontSize=12;"
)

NODE_EXTERNAL = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#999999;fontColor=#ffffff;strokeColor=#8A8A8A;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

NODE_SECURITY = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E74C3C;fontColor=#ffffff;strokeColor=#C0392B;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

NODE_NETWORKING = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#7B1FA2;fontColor=#ffffff;strokeColor=#6A1B9A;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

NODE_MONITORING = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#999999;fontColor=#ffffff;strokeColor=#8A8A8A;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

NODE_PERSON = (
    "shape=mxgraph.c4.person2;whiteSpace=wrap;html=1;"
    "align=center;metaEdit=1;"
    "fillColor=#08427B;fontColor=#ffffff;strokeColor=#073763;fontSize=12;"
)

# Semantic role name → style string
NODE_STYLES = {
    "compute": NODE_COMPUTE,
    "queue": NODE_QUEUE,
    "messaging": NODE_QUEUE,
    "database": NODE_DATABASE,
    "storage": NODE_DATABASE,
    "external": NODE_EXTERNAL,
    "security": NODE_SECURITY,
    "networking": NODE_NETWORKING,
    "monitoring": NODE_MONITORING,
    "person": NODE_PERSON,
}

# ---------------------------------------------------------------------------
# Node styles — C4 component level colors
# ---------------------------------------------------------------------------

C4_COMPONENT_HANDLER = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#438DD5;fontColor=#ffffff;strokeColor=#3C7FC0;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

C4_COMPONENT_VALIDATOR = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#4CAF50;fontColor=#ffffff;strokeColor=#388E3C;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

C4_COMPONENT_CACHE = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E8A735;fontColor=#ffffff;strokeColor=#C88B1E;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

C4_COMPONENT_SDK = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#7B1FA2;fontColor=#ffffff;strokeColor=#6A1B9A;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

C4_COMPONENT_CROSSCUTTING = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#999999;fontColor=#ffffff;strokeColor=#8A8A8A;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

# ---------------------------------------------------------------------------
# Node styles — C4 code level colors
# ---------------------------------------------------------------------------

C4_CODE_ENTRY = C4_COMPONENT_HANDLER  # same blue
C4_CODE_PURE = C4_COMPONENT_VALIDATOR  # same green
C4_CODE_IO = C4_COMPONENT_CACHE  # same orange

C4_CODE_STRUCT = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#F5F5F5;fontColor=#000000;strokeColor=#999999;"
    "arcSize=10;align=center;verticalAlign=middle;fontSize=12;"
)

C4_CODE_EXTERNAL_DEP = C4_COMPONENT_CROSSCUTTING  # same grey

# ---------------------------------------------------------------------------
# Special shapes
# ---------------------------------------------------------------------------

SHAPE_DECISION = (
    "shape=rhombus;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#000000;"
    "whiteSpace=wrap;html=1;"
)

SHAPE_START_END = (
    "ellipse;fillColor=#4CAF50;fontColor=#ffffff;strokeColor=#388E3C;"
    "whiteSpace=wrap;html=1;"
)

SHAPE_ERROR_END = (
    "ellipse;fillColor=#F44336;fontColor=#ffffff;strokeColor=#C0392B;"
    "whiteSpace=wrap;html=1;"
)

SHAPE_PARALLELOGRAM = (
    "shape=parallelogram;fillColor=#E0E0E0;strokeColor=#999999;"
    "fontColor=#000000;whiteSpace=wrap;html=1;"
)

SHAPE_HEXAGON = (
    "shape=hexagon;fillColor=#E0E0E0;strokeColor=#999999;"
    "fontColor=#000000;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;"
)

SHAPE_UML_CLASS = (
    "swimlane;fontStyle=1;align=center;startSize=26;html=1;"
    "fillColor=#F5F5F5;strokeColor=#999999;fontColor=#000000;"
)

# ---------------------------------------------------------------------------
# Edge styles — by interaction type
# ---------------------------------------------------------------------------

EDGE_SYNC = (
    "endArrow=blockThin;html=1;fontSize=11;"
    "fontColor=#707070;strokeColor=#707070;"
    "endFill=1;edgeStyle=orthogonalEdgeStyle;curved=1;"
)

EDGE_ASYNC_RESPONSE = (
    "endArrow=open;html=1;fontSize=11;"
    "fontColor=#707070;strokeColor=#707070;"
    "dashed=1;dashPattern=8 4;edgeStyle=orthogonalEdgeStyle;curved=1;"
)

EDGE_ERROR = (
    "endArrow=blockThin;html=1;fontSize=11;"
    "fontColor=#F44336;strokeColor=#F44336;"
    "endFill=1;edgeStyle=orthogonalEdgeStyle;curved=1;"
)

EDGE_ERROR_RESPONSE = (
    "endArrow=open;html=1;fontSize=11;"
    "fontColor=#F44336;strokeColor=#F44336;"
    "dashed=1;dashPattern=8 4;edgeStyle=orthogonalEdgeStyle;curved=1;"
)

EDGE_RETRY = (
    "endArrow=blockThin;html=1;fontSize=11;"
    "fontColor=#FF9800;strokeColor=#FF9800;"
    "dashed=1;dashPattern=8 4;edgeStyle=orthogonalEdgeStyle;curved=1;"
)

EDGE_ROLLBACK = (
    "endArrow=open;html=1;fontSize=11;"
    "fontColor=#F44336;strokeColor=#F44336;"
    "dashed=1;dashPattern=8 4;edgeStyle=orthogonalEdgeStyle;curved=1;"
)

EDGE_DATA_FLOW = (
    "endArrow=blockThin;html=1;fontSize=11;"
    "fontColor=#4CAF50;strokeColor=#4CAF50;"
    "endFill=1;edgeStyle=orthogonalEdgeStyle;curved=1;"
)

EDGE_DEPENDENCY = (
    "endArrow=open;html=1;fontSize=10;"
    "fontColor=#999999;strokeColor=#999999;"
    "dashed=1;dashPattern=2 2;"
)

EDGE_NUMBERED = (
    "endArrow=blockThin;html=1;fontSize=11;"
    "fontColor=#707070;strokeColor=#707070;endFill=1;"
)

# For sequence diagram messages (no orthogonal routing)
EDGE_SEQ_REQUEST = (
    "endArrow=blockThin;html=1;fontSize=11;"
    "fontColor=#707070;strokeColor=#707070;endFill=1;"
)

EDGE_SEQ_RESPONSE = (
    "endArrow=open;html=1;fontSize=11;"
    "fontColor=#707070;strokeColor=#707070;"
    "dashed=1;dashPattern=8 4;"
)

EDGE_SEQ_ERROR = (
    "endArrow=blockThin;html=1;fontSize=11;"
    "fontColor=#F44336;strokeColor=#F44336;endFill=1;"
)

EDGE_STYLES = {
    "sync": EDGE_SYNC,
    "async": EDGE_ASYNC_RESPONSE,
    "error": EDGE_ERROR,
    "error_response": EDGE_ERROR_RESPONSE,
    "retry": EDGE_RETRY,
    "rollback": EDGE_ROLLBACK,
    "data_flow": EDGE_DATA_FLOW,
    "dependency": EDGE_DEPENDENCY,
    "numbered": EDGE_NUMBERED,
    "seq_request": EDGE_SEQ_REQUEST,
    "seq_response": EDGE_SEQ_RESPONSE,
    "seq_error": EDGE_SEQ_ERROR,
}

# ---------------------------------------------------------------------------
# Lifeline style (sequence diagrams — must be edge, not vertex)
# ---------------------------------------------------------------------------

LIFELINE = (
    "endArrow=none;html=1;"
    "strokeColor=#CCCCCC;strokeWidth=1;"
    "dashed=1;dashPattern=4 4;"
)

# ---------------------------------------------------------------------------
# Activation bar (sequence diagrams)
# ---------------------------------------------------------------------------

ACTIVATION_BAR = (
    "rounded=0;whiteSpace=wrap;html=1;"
    "fillColor=#E6E6E6;strokeColor=#999999;"
)

# ---------------------------------------------------------------------------
# Groups / sections
# ---------------------------------------------------------------------------

GROUP_SUCCESS = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E8F5E9;strokeColor=#4CAF50;"
    "opacity=40;dashed=0;verticalAlign=top;align=left;"
    "spacingTop=8;spacingLeft=10;fontSize=14;fontStyle=1;fontColor=#4CAF50;"
)

GROUP_INFO = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E3F2FD;strokeColor=#2196F3;"
    "opacity=40;dashed=0;verticalAlign=top;align=left;"
    "spacingTop=8;spacingLeft=10;fontSize=14;fontStyle=1;fontColor=#2196F3;"
)

GROUP_WARNING = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFF3E0;strokeColor=#FF9800;"
    "opacity=40;dashed=0;verticalAlign=top;align=left;"
    "spacingTop=8;spacingLeft=10;fontSize=14;fontStyle=1;fontColor=#FF9800;"
)

GROUP_DANGER = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFEBEE;strokeColor=#F44336;"
    "opacity=40;dashed=0;verticalAlign=top;align=left;"
    "spacingTop=8;spacingLeft=10;fontSize=14;fontStyle=1;fontColor=#F44336;"
)

GROUP_STYLES = {
    "success": GROUP_SUCCESS,
    "info": GROUP_INFO,
    "warning": GROUP_WARNING,
    "danger": GROUP_DANGER,
}

# ---------------------------------------------------------------------------
# Trust boundaries (threat model)
# ---------------------------------------------------------------------------

TRUST_UNTRUSTED = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFEBEE;strokeColor=#F44336;"
    "strokeWidth=2;dashed=1;dashPattern=8 4;"
    "arcSize=6;opacity=30;fontSize=14;fontStyle=1;fontColor=#F44336;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
)

TRUST_SEMI = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFF3E0;strokeColor=#FF9800;"
    "strokeWidth=2;dashed=1;dashPattern=8 4;"
    "arcSize=6;opacity=30;fontSize=14;fontStyle=1;fontColor=#FF9800;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
)

TRUST_TRUSTED = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E8F5E9;strokeColor=#4CAF50;"
    "strokeWidth=2;dashed=1;dashPattern=8 4;"
    "arcSize=6;opacity=30;fontSize=14;fontStyle=1;fontColor=#4CAF50;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
)

# ---------------------------------------------------------------------------
# Infrastructure boundaries
# ---------------------------------------------------------------------------

BOUNDARY_REGION = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#F5F5F5;strokeColor=#9E9E9E;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
    "fontSize=14;fontStyle=1;fontColor=#666666;"
)

BOUNDARY_VPC = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=none;strokeColor=#1565C0;"
    "dashed=1;dashPattern=8 4;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
    "fontSize=14;fontStyle=1;fontColor=#1565C0;"
)

BOUNDARY_PUBLIC_SUBNET = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E8F5E9;strokeColor=#4CAF50;opacity=60;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
    "fontSize=14;fontStyle=1;fontColor=#4CAF50;"
)

BOUNDARY_PRIVATE_SUBNET = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E3F2FD;strokeColor=#1976D2;opacity=60;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
    "fontSize=14;fontStyle=1;fontColor=#1976D2;"
)

BOUNDARY_SECURITY_GROUP = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=none;strokeColor=#999999;"
    "dashed=1;dashPattern=2 2;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
    "fontSize=12;fontStyle=0;fontColor=#999999;"
)

# ---------------------------------------------------------------------------
# C4 container boundary
# ---------------------------------------------------------------------------

BOUNDARY_C4_CONTAINER = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=none;strokeColor=#666666;"
    "dashed=1;dashPattern=8 4;"
    "fontSize=14;fontStyle=1;fontColor=#444444;"
    "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;"
)

# ---------------------------------------------------------------------------
# Internal processing boxes (sequence diagrams)
# ---------------------------------------------------------------------------

INTERNAL_NORMAL = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E3F2FD;strokeColor=#2196F3;fontColor=#000000;"
    "fontSize=10;align=center;verticalAlign=middle;"
)

INTERNAL_CONDITIONAL = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFF3E0;strokeColor=#FF9800;fontColor=#000000;"
    "fontSize=10;align=center;verticalAlign=middle;"
)

INTERNAL_ERROR = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFEBEE;strokeColor=#F44336;fontColor=#000000;"
    "fontSize=10;align=center;verticalAlign=middle;"
)

INTERNAL_VALIDATION = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E8F5E9;strokeColor=#4CAF50;fontColor=#000000;"
    "fontSize=10;align=center;verticalAlign=middle;"
)

# ---------------------------------------------------------------------------
# Text elements
# ---------------------------------------------------------------------------

TEXT_TITLE = (
    "text;html=1;align=center;verticalAlign=middle;"
    "resizable=0;points=[];autosize=1;"
    "strokeColor=none;fillColor=none;"
    "fontSize=18;fontStyle=1;fontColor=#333333;"
)

TEXT_SUBTITLE = (
    "text;html=1;align=center;verticalAlign=middle;"
    "resizable=0;points=[];autosize=1;"
    "strokeColor=none;fillColor=none;"
    "fontSize=12;fontStyle=0;fontColor=#666666;"
)

TEXT_CAPTION = (
    "text;html=1;align=center;verticalAlign=middle;"
    "resizable=0;points=[];autosize=1;"
    "strokeColor=none;fillColor=none;"
    "fontSize=11;fontStyle=2;fontColor=#666666;"
)

TEXT_LEGEND = (
    "text;html=1;fontSize=10;fontColor=#666666;"
    "align=left;verticalAlign=middle;"
)

TEXT_GROUP_LABEL = (
    "text;html=1;align=left;verticalAlign=middle;"
    "resizable=0;points=[];autosize=1;"
    "strokeColor=none;fillColor=none;"
    "fontSize=14;fontStyle=1;"
)

# ---------------------------------------------------------------------------
# Legend container
# ---------------------------------------------------------------------------

LEGEND_CONTAINER = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FAFAFA;strokeColor=#E0E0E0;"
    "fontSize=11;fontColor=#666666;"
    "verticalAlign=top;align=left;spacingTop=4;spacingLeft=8;"
)

# ---------------------------------------------------------------------------
# ERD entity header colors (by store type)
# ---------------------------------------------------------------------------

ERD_RELATIONAL = (
    "swimlane;fontStyle=1;align=center;startSize=26;html=1;"
    "fillColor=#E3F2FD;strokeColor=#438DD5;fontColor=#000000;"
)

ERD_NOSQL = (
    "swimlane;fontStyle=1;align=center;startSize=26;html=1;"
    "fillColor=#FFF3E0;strokeColor=#E8A735;fontColor=#000000;"
)

ERD_CACHE = (
    "swimlane;fontStyle=1;align=center;startSize=26;html=1;"
    "fillColor=#E8F5E9;strokeColor=#4CAF50;fontColor=#000000;"
)

ERD_SEARCH = (
    "swimlane;fontStyle=1;align=center;startSize=26;html=1;"
    "fillColor=#F3E5F5;strokeColor=#7B1FA2;fontColor=#000000;"
)

ERD_FIELD = (
    "text;html=1;align=left;verticalAlign=middle;"
    "strokeColor=none;fillColor=none;"
    "fontSize=11;fontColor=#333333;"
)

ERD_STYLES = {
    "relational": ERD_RELATIONAL,
    "nosql": ERD_NOSQL,
    "cache": ERD_CACHE,
    "search": ERD_SEARCH,
}

# ---------------------------------------------------------------------------
# CI/CD specific
# ---------------------------------------------------------------------------

CICD_TRIGGER = (
    "ellipse;fillColor=#616161;fontColor=#ffffff;strokeColor=#424242;"
    "whiteSpace=wrap;html=1;"
)

CICD_QUALITY_GATE = (
    "shape=rhombus;fillColor=#FFEBEE;strokeColor=#F44336;"
    "fontColor=#000000;whiteSpace=wrap;html=1;"
)

FORK_JOIN_BAR = (
    "shape=line;html=1;strokeWidth=3;"
    "strokeColor=#333333;fillColor=none;"
)

# ---------------------------------------------------------------------------
# Data flow state progression colors
# ---------------------------------------------------------------------------

DATA_STATE_RAW = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFEBEE;strokeColor=#F44336;fontColor=#000000;"
    "arcSize=10;align=left;verticalAlign=top;fontSize=11;spacingLeft=6;spacingTop=6;"
)

DATA_STATE_PARSED = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFF3E0;strokeColor=#E8A735;fontColor=#000000;"
    "arcSize=10;align=left;verticalAlign=top;fontSize=11;spacingLeft=6;spacingTop=6;"
)

DATA_STATE_VALIDATED = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#FFF8E1;strokeColor=#FFC107;fontColor=#000000;"
    "arcSize=10;align=left;verticalAlign=top;fontSize=11;spacingLeft=6;spacingTop=6;"
)

DATA_STATE_ENRICHED = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E8F5E9;strokeColor=#4CAF50;fontColor=#000000;"
    "arcSize=10;align=left;verticalAlign=top;fontSize=11;spacingLeft=6;spacingTop=6;"
)

DATA_STATE_STORED = (
    "rounded=1;whiteSpace=wrap;html=1;"
    "fillColor=#E3F2FD;strokeColor=#438DD5;fontColor=#000000;"
    "arcSize=10;align=left;verticalAlign=top;fontSize=11;spacingLeft=6;spacingTop=6;"
)

# ---------------------------------------------------------------------------
# Geometry defaults
# ---------------------------------------------------------------------------

DEFAULT_NODE_WIDTH = 160
DEFAULT_NODE_HEIGHT = 80
PERSON_WIDTH = 200
PERSON_HEIGHT = 180
LARGE_SYSTEM_WIDTH = 300
LARGE_SYSTEM_HEIGHT = 160
DECISION_WIDTH = 120
DECISION_HEIGHT = 80
START_END_WIDTH = 100
START_END_HEIGHT = 40

NODE_SPACING_H = 60  # horizontal gap between nodes
NODE_SPACING_V = 60  # vertical gap between nodes
GROUP_PADDING = 40  # padding inside group boundaries

# Sequence diagram geometry
SEQ_PARTICIPANT_WIDTH = 140
SEQ_PARTICIPANT_HEIGHT = 50
SEQ_PARTICIPANT_SPACING = 200  # center-to-center
SEQ_MESSAGE_Y_SPACING = 40
SEQ_MESSAGE_Y_START = 40  # below lifeline top
SEQ_LIFELINE_START_Y = 80  # below participant box bottom

# ERD geometry
ERD_ENTITY_WIDTH = 200
ERD_ENTITY_HEADER_HEIGHT = 26
ERD_FIELD_HEIGHT = 20
ERD_ENTITY_SPACING = 80
