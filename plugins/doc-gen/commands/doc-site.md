# /doc-site — Build Static HTML Site

Convert markdown documentation with Mermaid diagrams into a static HTML site using `mkdocs build`. The mkdocs-drawio-plugin converts Mermaid blocks to interactive draw.io embeds.

## Instructions

You are running the `/doc-site` command — Phase 2 of documentation generation.

**This command runs `mkdocs build` to convert Phase 1 markdown output (with Mermaid diagrams) into a polished HTML site with interactive draw.io diagram embeds.**

### Prerequisites

Check that `docs/md/` contains markdown files (Glob: `docs/md/*.md`). If empty or missing, tell the user to run `/doc-generate` first and stop.

### Step 1: Verify Build Tools

1. Check `mkdocs.yml` exists in the project root
2. Verify mkdocs is installed: `mkdocs --version`
3. Verify mkdocs-drawio-plugin is installed: `pip show mkdocs-drawio-plugin`

If any are missing, tell the user what to install and stop.

### Step 2: Inventory & Plan

Glob `docs/md/*.md` to list all markdown files. For each file, Grep for `` ```mermaid `` to count diagrams.

Display:
```
Site Generation Plan
=====================
Markdown files: {count}
Pages with Mermaid diagrams: {count_with_diagrams}
Total Mermaid blocks: {total_diagrams}
Build tool: mkdocs build (with mkdocs-drawio-plugin)

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
  - API Plane:
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

This converts all markdown to HTML and all Mermaid blocks to draw.io embeds.

### Step 6: Verify Output

1. Count HTML pages: Glob `docs/site/**/*.html`
2. Count draw.io embeds: Grep for `class="mxgraph"` across all HTML
3. Check for unconverted Mermaid: Grep for `` ```mermaid `` in HTML — CRITICAL if found
4. Check for legacy markers: Grep for `<!-- diagram-meta` or `<!-- diagram:` in HTML — CRITICAL if found

### Step 7: Run Validation

1. Locate `{SKILLS_DIR}/doc-validate-site/SKILL.md` if it exists
2. Spawn a Task agent to do site-wide validation
3. Display validation results

### Step 8: Summary

```
Site Generation Complete
=========================
Total HTML pages: {count}
Total draw.io embeds: {diagram_count}
Unconverted Mermaid blocks: {count} (must be 0)

Site location: docs/site/
File URL: file://{absolute_path}/docs/site/index.html

Validation: {PASS/FAIL}

To view: open docs/site/index.html
```

### Error Handling

- If `mkdocs build` fails, display the error output and suggest fixes
- If the mkdocs-drawio-plugin is not installed, tell user to install it: `pip install -e ./mkdocs-drawio-plugin`
- Report all failures in the summary with specific error details

### Important Rules

- **ZERO unconverted Mermaid blocks in final HTML** — every Mermaid block must be converted by the plugin
- **ZERO legacy diagram markers** — if found, Phase 1 skills need re-running
- Use `subagent_type: "general-purpose"` for all agents
