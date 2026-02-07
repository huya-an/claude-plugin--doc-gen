# doc-site

## Description
Phase 2 site generator: runs `mkdocs build` to convert markdown documentation into a static HTML site. Mermaid diagrams render client-side via Mermaid.js with interactive pan/zoom and click-to-fullscreen modal.

## Context
fork

## References
- references/mermaid-init.js
- references/diagram-viewer.js

## Instructions

You are the **Site Generator Agent**. Your ONLY job is to run `mkdocs build`. You MUST NOT manually convert markdown to HTML.

### Critical Rule

**NEVER manually convert markdown to HTML.** Always use `mkdocs build`. MkDocs handles all conversion, templating, navigation, and styling. Your job is to:
1. Verify prerequisites
2. Configure `mkdocs.yml` if needed
3. Run `mkdocs build`
4. Verify the output

That's it. No custom HTML generation. No manual file conversion.

### Step 1: Verify Prerequisites

#### Check for markdown files
Glob `docs/md/*.md`. If empty or missing, tell the user to run `/doc-generate` first and stop.

#### Check mkdocs installation
Run: `which mkdocs`

If mkdocs is NOT installed, use AskUserQuestion to ask:
```
MkDocs is required but not installed. How would you like to proceed?

Options:
1. Install now (pip install mkdocs mkdocs-material pymdown-extensions)
2. I'll install it manually
```

If user chooses option 1, run:
```bash
pip install mkdocs mkdocs-material pymdown-extensions
```

Then verify again with `which mkdocs`. If still not found, stop and tell user to check their Python/pip setup.

### Step 2: Read Project Metadata

1. Read `docs/.doc-plan.json` — get project name and metadata
2. Glob `docs/md/*.md` — get all markdown files
3. Read frontmatter from each markdown file to build navigation (read in batches of 5 to stay within context limits)

### Step 3: Create or Update mkdocs.yml

If `mkdocs.yml` does not exist in the project root, create it. If it exists, update the `nav:` section only — preserve user customizations to theme/plugins.

```yaml
site_name: {Project Name} Documentation
docs_dir: docs/md
site_dir: docs/site

use_directory_urls: false

theme:
  name: material
  features:
    - navigation.instant
    - navigation.sections
    - navigation.top
    - navigation.prune
    - search.highlight
    - content.code.copy
  palette:
    scheme: default
    primary: blue
    accent: blue

plugins:
  - search

markdown_extensions:
  - toc:
      permalink: true
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid-raw
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - attr_list
  - md_in_html
  - tables

extra_javascript:
  - https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js
  - js/mermaid-init.js
  - js/diagram-viewer.js

extra_css:
  - css/custom.css

nav:
  # Will be generated from frontmatter
```

**Mermaid loading order:** Three scripts load in this exact order: (1) Mermaid UMD from CDN defines the global `mermaid` object, (2) `mermaid-init.js` unwraps the `<code>` tags pymdownx.superfences adds and calls `mermaid.run()`, (3) `diagram-viewer.js` adds pan/zoom/fullscreen to rendered SVGs. Use the UMD build (not ESM) so the site works from both `file://` and `https://`. Pin to a specific version to avoid breaking changes.

### Step 3a: Create Diagram Assets

Create three JS/CSS files that handle Mermaid rendering and diagram interactivity.

#### Create `docs/md/js/mermaid-init.js`

> **CRITICAL: This file MUST be created. Without it, Mermaid diagrams will NOT render.**

pymdownx.superfences renders mermaid blocks as `<pre class="mermaid-raw"><code>...source...</code></pre>`. Mermaid.js cannot parse the `<code>` wrapper. This init script unwraps it and triggers rendering.

Write the file using the **exact content** from the `mermaid-init.js` reference. This script:
- Assumes the global `mermaid` object is already available (loaded via CDN UMD build)
- Unwraps `<code>` tags from `<pre class="mermaid-raw">` elements
- Calls `mermaid.run()` to render diagrams
- Supports MkDocs Material instant navigation via `document$`

#### Create `docs/md/js/diagram-viewer.js`

> **CRITICAL: You MUST also create `diagram-viewer.js` from the reference. mermaid-init.js handles rendering; diagram-viewer.js handles interactivity (pan/zoom/fullscreen). These are two separate files with two separate concerns.**

Write the file using the **exact content** from the `diagram-viewer.js` reference. This script:
- Waits for Mermaid.js to render SVGs, then enhances each diagram container
- Adds an expand button overlay and "click to expand" hint
- On click, opens a fullscreen dark modal with the diagram at full size
- Supports mouse wheel zoom (toward cursor), drag to pan, pinch-zoom on mobile
- Has zoom +/- buttons and a "Fit" reset button
- Closes on Escape, backdrop click, or close button
- Injects its own CSS — no external stylesheet dependency

#### Create `docs/md/css/custom.css`

```css
/* Responsive content width */
.md-grid { max-width: 90rem; }
.md-content { max-width: none; }

/* Diagram alignment */
.mermaid-raw { text-align: center; }
```

The responsive overrides ensure content uses available screen width instead of being locked to 976px. The diagram-viewer.js injects all interactive styles (borders, hover effects, modal, controls) at runtime. If the viewer JS fails to load, diagrams still render normally.

### Step 4: Generate Navigation from Frontmatter

Read frontmatter from all markdown files. Build a `nav:` section using `section`, `subsection` (optional), and `order` fields.

#### Navigation Algorithm

1. **Group by section** — collect all files by their `section` value
2. **Within each section, split by subsection**:
   - Files with no `subsection` go directly under the section
   - Files with `subsection` are nested. Split the `subsection` value on `/` to create sub-levels.
   - Example: `subsection: "PostgreSQL/Tables"` creates `section > PostgreSQL > Tables > page`
3. **Order within each group** by the `order` frontmatter value (ascending)
4. **Use the `title`** from frontmatter as the nav label

#### Example with hierarchical data pages

Given frontmatter like:
```yaml
# data--overview.md: section "Data", no subsection, order 1
# data--pipelines.md: section "Data", no subsection, order 2
# data--postgres--overview.md: section "Data", subsection "PostgreSQL", order 1
# data--postgres--tables--users.md: section "Data", subsection "PostgreSQL/Tables", order 2
# data--postgres--tables--vehicle.md: section "Data", subsection "PostgreSQL/Tables", order 3
# data--postgres--queries--overview.md: section "Data", subsection "PostgreSQL/Queries", order 1
# data--postgres--queries--find-by-id-vehicle.md: section "Data", subsection "PostgreSQL/Queries", order 2
# data--dynamo--overview.md: section "Data", subsection "DynamoDB", order 1
```

Generates:
```yaml
nav:
  - Home: index.md
  - Architecture:
    - Overview: arch-overview.md
    - C4 Level 1 — System Context: arch-c4-level1.md
  - Data:
    - Overview: data--overview.md
    - Pipelines: data--pipelines.md
    - PostgreSQL:
      - Overview: data--postgres--overview.md
      - Tables:
        - users: data--postgres--tables--users.md
        - vehicle: data--postgres--tables--vehicle.md
      - Queries:
        - Overview: data--postgres--queries--overview.md
        - findByIdVehicle: data--postgres--queries--find-by-id-vehicle.md
    - DynamoDB:
      - Overview: data--dynamo--overview.md
  - Events:
    - Overview: events-overview.md
```

#### Backward compatibility

The `subsection` field is **optional**. Files without a `subsection` (the majority of non-data pages) work exactly as before — grouped by `section`, ordered by `order`, 2-level navigation. Only pages that include `subsection` get deeper nesting.

**Ordering rules:**
- Sections appear in wave order: Architecture → API → Data → Events → Security → DevOps → Testing → ADRs → Quality
- Within each section, non-subsection pages come first (ordered by `order`), then subsection groups
- Within each subsection group, pages are ordered by their `order` frontmatter value
- Use the `title` from frontmatter as the nav label
- ADR individual pages (adr-001.md, adr-002.md, etc.) are listed under the ADRs section after the index
- `index.md` always comes first as "Home"

> **CRITICAL: Every markdown file MUST have its own nav entry. Never collapse a subsection group into a single overview link. If there are 164 query files, there must be 164 nav entries under that subsection. A missing nav entry means the page is unreachable from navigation.**

Update the `nav:` section in `mkdocs.yml` with the generated navigation.

### Step 5: Create Index Page

If `docs/md/index.md` does not exist (it should have been created by doc-generate), create a minimal one with:
- Project name from `.doc-plan.json`
- Brief description
- Links to each section's overview page
- Generation date

### Step 6: Run MkDocs Build

```bash
mkdocs build
```

This single command does everything:
- Converts all markdown to HTML
- Applies Material for MkDocs theme
- Generates navigation, search index, and sitemap
- Preserves Mermaid blocks as `<pre class="mermaid-raw">` for client-side rendering
- Outputs to `docs/site/`

**Do not add any post-processing steps.** MkDocs output is final.

**If the build fails:**
1. Read the error output — MkDocs gives specific error messages
2. Common issues:
   - Missing markdown extension: install it with pip
   - YAML syntax error in mkdocs.yml: fix the YAML
   - Missing file referenced in nav: remove it from nav or create a placeholder
3. Fix the issue and re-run `mkdocs build`

### Step 7: Verify Output

After the build completes:

1. **Count HTML pages**: Glob `docs/site/**/*.html` — compare against markdown file count
2. **Verify Mermaid blocks**: Grep for `class="mermaid-raw"` in HTML files — should match markdown Mermaid block count
3. **Verify diagram viewer**: Confirm `docs/site/js/diagram-viewer.js` exists (enables pan/zoom + fullscreen)
4. **Check for legacy markers**: Grep for `<!-- diagram-meta` or `<!-- diagram:` — CRITICAL if found
5. **Verify navigation**: Read `docs/site/index.html` to confirm sidebar navigation was generated

Display:
```
Site Build Complete
====================
HTML pages: {count} (from {md_count} markdown files)
Mermaid diagram blocks: {count}
Legacy diagram markers: {count} (must be 0)
Navigation sections: {count}

Site location: docs/site/
Open: file://{absolute_path}/docs/site/index.html
```

### Rules

1. **Always use `mkdocs build`** — never manually convert markdown to HTML
2. **Mermaid.js renders client-side** — no server-side diagram conversion
3. **Do not modify HTML after build** — MkDocs output is final
4. **Zero legacy markers** — if any `<!-- diagram:` markers remain, Phase 1 needs re-running
5. **Pin Mermaid.js version** — use a specific version number, not a floating tag
6. **Preserve user config** — if mkdocs.yml already exists, only update the nav section

## Tools
- Read
- Glob
- Grep
- Write
- Edit
- Bash (for running mkdocs build and pip install)
- AskUserQuestion (for missing prerequisites)

## Output
- Complete static site in `docs/site/` (generated by mkdocs build)
- Updated `mkdocs.yml` with navigation
- `docs/md/js/diagram-viewer.js` — interactive pan/zoom + fullscreen modal for diagrams
- `docs/md/css/custom.css` — base diagram styles
