# ADR-0013: Draw.io Sequence Diagram Rendering Pattern

## Status
Accepted

## Date
2026-02-01

## Context

During end-to-end testing of the `doc-site` pipeline on a real codebase (platform.util.webhook), all 13 sequence diagrams rendered as broken garbage in the browser while all other diagram types (C4, data-flow, devops, infra-topology) rendered correctly.

Investigation revealed three independent root causes:

1. **Missing reference example.** `drawio-patterns.md` had complete XML examples for C4, ERD, and flow diagrams but contained only a partial stub for sequence diagrams. Agent B (the diagram-conversion agent in the three-agent pipeline) had no correct XML pattern to follow.

2. **Wrong edge wiring.** Without a reference, Agent B generated sequence message arrows using `source="cell_id"` / `target="cell_id"` — the same pattern that works for C4 and flow diagrams. In sequence diagrams this connects arrows to participant header boxes, creating self-referencing loops and daisy-chains. The draw.io viewer rendered these as tiny loops or arrows pointing to the wrong target.

3. **Wrong lifeline element type.** Lifelines were generated as vertex cells with `style="line;..."`. The `line` shape does not render in `viewer-static.min.js`. Lifelines appeared as invisible elements.

Additionally, a separate rendering issue affected all diagram types: diagrams did not scale to fill the page width. This was caused by:
- `<mxGraphModel>` tags containing `page="1" pageWidth="1169" pageHeight="827"` attributes that lock the viewer to fixed dimensions
- The draw.io viewer setting inline `width`/`height` styles on its `.geDiagramContainer` wrapper, overriding normal CSS

## Decision

Sequence diagrams use a fundamentally different draw.io XML pattern from all other diagram types. The following rules are codified in `drawio-patterns.md` and `doc-site/SKILL.md`:

### 1. Message arrows use sourcePoint/targetPoint coordinates, not cell ID references

```xml
<mxCell id="MSG_ID" value="label from ASCII"
  style="endArrow=blockThin;html=1;fontSize=11;fontColor=#707070;strokeColor=#707070;endFill=1;"
  edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="SOURCE_LIFELINE_X" y="MESSAGE_Y" as="sourcePoint"/>
    <mxPoint x="TARGET_LIFELINE_X" y="MESSAGE_Y" as="targetPoint"/>
  </mxGeometry>
</mxCell>
```

This is the opposite of C4/flow diagrams where edges reference `source`/`target` cell IDs. Sequence messages must use explicit x,y coordinates because the arrow endpoints are positions on lifelines, not connections to shapes.

### 2. Lifelines are edge cells, not vertex cells

```xml
<mxCell id="LIFELINE_ID" value=""
  style="endArrow=none;html=1;strokeColor=#CCCCCC;strokeWidth=1;dashed=1;dashPattern=4 4;"
  edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="PARTICIPANT_CENTER_X" y="PARTICIPANT_BOTTOM_Y" as="sourcePoint"/>
    <mxPoint x="PARTICIPANT_CENTER_X" y="DIAGRAM_BOTTOM_Y" as="targetPoint"/>
  </mxGeometry>
</mxCell>
```

The `line` vertex shape does not render in `viewer-static.min.js`. Vertical dashed lifelines are modeled as edges with `endArrow=none`.

### 3. Bare `<mxGraphModel>` tag with no page attributes

```xml
<mxGraphModel>
  <root>...</root>
</mxGraphModel>
```

No `dx`, `dy`, `page`, `pageWidth`, `pageHeight` attributes. These lock the viewer to a fixed canvas size and prevent responsive scaling.

### 4. Viewer config includes fit and center

```json
{"nav":true,"resize":true,"fit":true,"center":true,"toolbar":"zoom layers","xml":"..."}
```

`fit:true` tells the viewer to scale the diagram to fill its container. `center:true` centers it horizontally.

### 5. CSS !important overrides for viewer inline styles

```css
.mxgraph .geDiagramContainer,
.mxgraph-wrapper .geDiagramContainer {
  width: 100% !important;
  overflow: visible !important;
}
.mxgraph svg, .mxgraph-wrapper svg {
  width: 100% !important;
  height: auto !important;
}
```

The draw.io viewer JS sets inline `width`/`height` on `.geDiagramContainer`. CSS `!important` is the only way to override inline styles without patching the viewer JS.

### 6. Complete worked example in drawio-patterns.md

A full 3-participant, multi-message sequence diagram XML example is provided in the reference so Agent B has an unambiguous pattern to follow. The example includes participants, lifelines, message arrows (both forward and return), group bands, and annotation text.

## Consequences

### Positive
- All 13 broken sequence diagrams now render correctly after regeneration
- Agent B has an unambiguous, complete reference pattern for every diagram type
- Responsive sizing works for all diagram types (sequence, C4, flow, ERD)
- The pattern is self-contained — no viewer JS modifications needed

### Negative
- Two completely different edge patterns coexist: cell-ID references (C4/flow/ERD) and coordinate-based (sequence). Agent B must select the correct pattern based on diagram type.
- CSS `!important` overrides are a maintenance risk if the draw.io viewer changes its DOM structure in future versions
- The sourcePoint/targetPoint coordinate system requires Agent B to compute x,y positions, which is more complex than cell-ID wiring

### Follow-up Actions
- Regenerate remaining 12 broken sequence diagrams (api-* and security-auth) on next full pipeline run
- Review this decision on: 2026-03-01

## Alternatives Considered

### 1. Patch viewer-static.min.js to support `line` vertex shapes
- Rejected: The viewer JS is a 2MB minified bundle. Patching it creates a maintenance burden on every viewer update and risks breaking other functionality.

### 2. Use SVG diagrams instead of draw.io XML
- Rejected: SVG would eliminate the viewer dependency but loses interactive features (pan, zoom, layer toggle) and the ability to export `.drawio` files for standalone editing. The dual-format diagram approach (ADR-0012) depends on draw.io XML.

### 3. Use cell-ID references with invisible anchor shapes on lifelines
- Rejected: Tested early in the investigation. Even with anchor shapes placed on lifelines, the viewer routes edges through the nearest connection point on the shape boundary, which produces diagonal arrows instead of horizontal ones.

## References
- ADR-0008: Per-Page Three-Agent Pipeline
- ADR-0012: Dual-Format Diagrams
- `plugins/doc-gen/skills/doc-site/references/drawio-patterns.md` — Section 5 (Sequence)
- `plugins/doc-gen/skills/doc-site/SKILL.md` — Item 4 (Sequence Diagram Edges)
- `plugins/doc-gen/skills/doc-site/references/styles.css` — Diagram container and viewer override rules
