# Claude Doc Gen

A Claude Code plugin that generates comprehensive documentation for any codebase.

## What It Does

Analyzes your codebase and produces:
- **C4 Architecture diagrams** (all 4 levels: Context, Container, Component, Code)
- **API documentation** with per-endpoint pages and sequence diagrams
- **Architecture Decision Records** (existing or inferred from code)
- **Security analysis** with authentication flows and threat models
- **DevOps documentation** with CI/CD pipeline and infrastructure diagrams
- **Data layer documentation** with ERD diagrams and schema docs
- **Event architecture** with event catalogs and flow diagrams
- **Testing strategy** with test inventory and coverage analysis
- **Code quality** with tech debt assessment and recommendations

Output is a static HTML site with interactive draw.io diagrams, viewable via `file://` in any browser. No web server needed.

## Installation

### Option 1: Install from GitHub (Recommended)

```bash
/plugin https://github.com/huya-an/claude-plugin--doc-gen
```

This will install the plugin directly from GitHub.

### Option 2: Manual Installation

Clone and symlink:

```bash
git clone https://github.com/huya-an/claude-plugin--doc-gen.git
ln -s "$(pwd)/claude-plugin--doc-gen" ~/.claude/plugins/claude-doc-gen
```

## Quick Start

Navigate to any codebase and run:

```
/doc
```

This scans your codebase and presents a documentation plan. Approve the sections you want, then:

```
/doc-generate
```

This generates markdown documentation. Finally:

```
/doc-site
```

This builds the static HTML site. Open it:

```bash
open docs/site/index.html
```

## Commands

| Command | Purpose |
|---------|---------|
| `/doc` | Discovery — scan codebase and create documentation plan |
| `/doc-generate` | Generate markdown documentation |
| `/doc-site` | Build static HTML site from markdown |
| `/doc-update` | Incremental update after code changes |
| `/doc-all` | Full pipeline: discovery → generate → site |
| `/doc-publish` | Publish site to S3 (requires AWS credentials) |

## How It Works

### Two-Phase Generation

**Phase 1 (Markdown):** Forked agents analyze source code and produce markdown files. Diagrams are Mermaid fenced code blocks.

**Phase 2 (HTML Site):** MkDocs with the mkdocs-drawio-plugin converts markdown to static HTML, replacing Mermaid blocks with interactive draw.io XML embeds. The draw.io viewer JS is bundled locally for offline viewing.

### Forked Agent Model

Every domain agent runs in a forked context (clean context window). This prevents token limit issues on large codebases — each agent only loads the files it needs to analyze.

### Wave-Based Execution

Documentation is generated in 4 sequential waves:
1. **Wave 1:** C4 architecture (system map — everything else depends on this)
2. **Wave 2:** API, Data, Events (horizontal concerns, run in parallel)
3. **Wave 3:** Security, DevOps, Testing (cross-cutting, reads Wave 1-2 output)
4. **Wave 4:** ADR, Quality (assessment, reads all prior waves)

### Supported Languages & Frameworks

Detection is automatic:
- **Java**: Spring Boot, Maven, Gradle
- **JavaScript/TypeScript**: Node.js, Express, Next.js, Angular, React
- **Python**: Django, Flask, FastAPI
- **Go**: Standard library, Gin, Echo
- **Rust**: Cargo-based projects
- **C#/.NET**: ASP.NET Core
- **Ruby**: Rails, Sinatra
- **PHP**: Laravel, Symfony

## Output Structure

```
docs/
├── .doc-plan.json              # Documentation plan
├── .doc-manifest.json          # File-to-section mapping
├── md/                         # Phase 1: Markdown output
│   ├── arch-overview.md
│   ├── arch-c4-level1.md
│   ├── api-index.md
│   └── ...
└── site/                       # Phase 2: Static HTML site
    ├── index.html              # Dashboard with stats
    ├── arch-overview.html
    ├── api-index.html
    ├── css/
    ├── js/
    │   └── viewer-static.min.js  # draw.io viewer (bundled)
    └── diagrams/
        └── *.drawio            # Editable diagram files
```

## Requirements

- Claude Code CLI
- Python 3.10+ (for MkDocs site generation)
- pip install mkdocs (if using `/doc-site`)

## License

MIT
