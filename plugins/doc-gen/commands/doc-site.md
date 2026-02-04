# /doc-site — Build Static HTML Site

Convert markdown documentation into a static HTML site using `mkdocs build`. Mermaid diagrams render client-side in the browser.

## Instructions

You are running the `/doc-site` command — Phase 2 of documentation generation.

**This command runs `mkdocs build` to convert Phase 1 markdown output into a polished HTML site.**

### Critical Rule

**NEVER manually convert markdown to HTML.** Always use `mkdocs build`. MkDocs handles all conversion, templating, navigation, and styling.

### Prerequisites

Check that `docs/md/` contains markdown files (Glob: `docs/md/*.md`). If empty or missing, tell the user to run `/doc-generate` first and stop.

### Step 1: Verify MkDocs Installation

Run: `which mkdocs`

If mkdocs is NOT installed, use AskUserQuestion:
```
MkDocs is required but not installed. How would you like to proceed?

Options:
1. Install now (Recommended) — runs: pip install mkdocs mkdocs-material pymdown-extensions
2. I'll install it manually
```

If user chooses option 1, run:
```bash
pip install mkdocs mkdocs-material pymdown-extensions
```

Verify installation with `which mkdocs`. If still not found, stop and tell user to check their Python/pip setup.

### Step 2: Inventory & Plan

Glob `docs/md/*.md` to list all markdown files. For each file, Grep for `` ```mermaid `` to count diagrams.

Display:
```
Site Generation Plan
=====================
Markdown files: {count}
Pages with Mermaid diagrams: {count_with_diagrams}
Total Mermaid blocks: {total_diagrams}
Build tool: mkdocs build

Starting site generation...
```

### Step 3: Generate Navigation

Read frontmatter from all markdown files. Build a `nav:` section for `mkdocs.yml` grouped by `section` and ordered by `order`:

```yaml
nav:
  - Home: index.md
  - Architecture:
    - Overview: arch-overview.md
    - C4 Level 1 — System Context: arch-c4-level1.md
    - C4 Level 2 — Containers: arch-c4-level2.md
  - API:
    - Endpoint Index: api-index.md
```

Update the `nav:` section in `mkdocs.yml`. Preserve other settings (theme, plugins, markdown_extensions, etc.).

### Step 4: Create Index Page

If `docs/md/index.md` does not exist, create it:
- Project name from `.doc-plan.json`
- Brief description
- Links to each section's overview page
- Generation date

### Step 5: Run MkDocs Build

```bash
mkdocs build
```

This single command:
- Converts all markdown to HTML
- Applies Material for MkDocs theme
- Generates navigation, search, and sitemap
- Preserves Mermaid blocks for client-side rendering
- Outputs to `docs/site/`

**Do not add any post-processing.** MkDocs output is final.

### Step 6: Verify Output

1. Count HTML pages: Glob `docs/site/**/*.html`
2. Verify Mermaid blocks: Grep for `class="mermaid"` in HTML
3. Check for legacy markers: Grep for `<!-- diagram-meta` or `<!-- diagram:` — CRITICAL if found

### Step 7: Summary

```
Site Generation Complete
=========================
Total HTML pages: {count}
Total Mermaid blocks: {diagram_count}
Legacy markers: {count} (must be 0)

Site location: docs/site/
File URL: file://{absolute_path}/docs/site/index.html

To view: open docs/site/index.html
```

### Error Handling

- If `mkdocs build` fails, display the error output and suggest fixes
- If mkdocs is not installed and user declines auto-install: `pip install mkdocs mkdocs-material pymdown-extensions`
- Report all failures in the summary with specific error details

### Important Rules

- **Always use `mkdocs build`** — never manually convert markdown to HTML
- **Mermaid.js renders client-side** — no server-side conversion needed
- **Do not modify HTML after build** — MkDocs output is final
- **Zero legacy markers** — if any `<!-- diagram:` markers remain, Phase 1 needs re-running
- Use `subagent_type: "general-purpose"` for all agents
