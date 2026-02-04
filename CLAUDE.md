# Claude Doc Gen - Plugin for Claude Code

This is a Claude Code plugin that generates comprehensive documentation for any codebase.

## Plugin Structure

- `plugins/doc-gen/skills/` — 14 specialized skills, each handling one documentation domain
- `plugins/doc-gen/commands/` — 6 user-facing commands (`/doc`, `/doc-generate`, `/doc-site`, `/doc-update`, `/doc-all`, `/doc-publish`)

## Architecture

### Two-Phase Generation

1. **Phase 1 (Markdown)**: Forked agents analyze source code and produce markdown files with Mermaid fenced code blocks (`` ```mermaid ``) for all diagrams
2. **Phase 2 (HTML Site)**: `mkdocs build` converts markdown to static HTML. Mermaid diagrams render client-side in the browser.

### Critical Rule

**NEVER manually convert markdown to HTML.** Always use `mkdocs build`. MkDocs handles all conversion, templating, navigation, and styling.

### Execution Model

- `/doc` — Discovery. Scans codebase structure (Glob + Grep only), presents a documentation plan for approval, saves `.doc-plan.json` and `.doc-manifest.json`
- `/doc-generate` — Wave-based execution (ADR-0010). 4 sequential waves, parallel within each wave. Later waves read prior wave markdown for context compression. Runs `doc-validate-md` after.
- `/doc-site` — Runs `mkdocs build` to convert markdown to HTML. Mermaid renders client-side.
- `/doc-update` — Incremental. Uses `git diff` to identify changed files, maps to affected sections, rebuilds only those in wave order. Runs `mkdocs build` for HTML rebuild.
- `/doc-all` — Full pipeline: discovery → wave-based generation → mkdocs build → optional S3 publish.

### Wave Ordering (ADR-0010)

- Wave 1: `doc-c4` (system map — everything else depends on this)
- Wave 2: `doc-api`, `doc-data`, `doc-events` (horizontal concerns, parallel)
- Wave 3: `doc-security`, `doc-devops`, `doc-testing` (cross-cutting, reads Wave 1-2 output)
- Wave 4: `doc-adr`, `doc-quality` (assessment, reads all prior waves)

### Key Conventions

- Every forked agent gets `context: fork` for a clean context window
- All diagrams are Mermaid fenced code blocks: `` ```mermaid ... ``` ``
- Supported Mermaid types: `C4Context`, `C4Container`, `C4Component`, `flowchart`, `sequenceDiagram`, `erDiagram`
- Shared Mermaid reference: `skills/references/mermaid-diagram-guide.md`
- All markdown files require frontmatter with `title`, `section`, `order`, `generated`
- Phase 2 uses `mkdocs build` — Mermaid diagrams render client-side via Mermaid.js
- **Always use `mkdocs build`** — never manually convert markdown to HTML
