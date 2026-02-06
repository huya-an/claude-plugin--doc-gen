# doc-validate-md

## Description
QA validation for Phase 1 markdown output. Validates Mermaid diagram blocks, frontmatter structure, content quality, cross-references, and adherence to skill output standards (Source Files sections, standardized tables, no content duplication). Reads files in batches.

## Context
fork

## Instructions

You are the **Markdown Validation Agent**. Validate every file in `docs/md/`.

**IMPORTANT: Read markdown files in batches of 5. Complete all checks for a batch before moving to the next. Do NOT read all files at once.**

### Phase 1: Plan Completeness

1. Read `docs/.doc-plan.json` — get expected output files per enabled section
2. Verify the plan has a `waves` object with keys `"1"` through `"4"` — if missing, report as WARNING (legacy plan format)
3. Glob `docs/md/*.md` — get actual files
4. Compare: report missing files (in plan but not generated) and extra files (generated but not in plan)

Initialize tracking:
- `frontmatter_issues = []`
- `diagram_issues = []`
- `crossref_issues = []`
- `content_issues = []`
- `structure_issues = []`

### Phase 2: Validate Files in Batches

Split the file list into batches of 5. For each batch, read all files and check:

1. **Frontmatter** — has `title` (non-empty string), `section` (non-empty), `order` (positive integer), `generated` (date string). ADR files additionally have `adr_status`, `adr_date`, `adr_inferred`.
2. **Mermaid diagram blocks** — every `` ```mermaid `` has a matching closing `` ``` ``. Inside each block:
   - First line declares a valid type: `C4Context`, `C4Container`, `C4Component`, `flowchart`, `sequenceDiagram`, `erDiagram`, `stateDiagram-v2`
   - Non-empty content (at least 2 lines after the type declaration)
   - No empty Mermaid blocks
3. **Legacy format detection (CRITICAL)** — check for any of these legacy markers which indicate unconverted content:
   - `<!-- diagram-meta` → CRITICAL (old dual-format YAML metadata)
   - `<!-- diagram:` → CRITICAL (old diagram marker format)
   - `end-diagram-meta` → CRITICAL
   - `<!-- end-diagram` → CRITICAL
   If any legacy markers are found, report as CRITICAL — these indicate the skill was not updated to Mermaid format.
4. **Cross-references** — every `[text](target.md)` link points to a file that exists in `docs/md/`
5. **Content quality** — no "TODO", "TBD", "Lorem ipsum", "placeholder" text. File has more than just frontmatter and a heading. Code blocks are properly fenced.
6. **Source Files section** — every file (except `index.md`) should have a `## Source Files` section near the end. Report as WARNING if missing.
7. **Standardized tables** — check that inventory/count tables include:
   - A **Total** row (for tables with counts/percentages)
   - **Percentage** column where counts are listed
   Report as INFO if missing (not blocking, but notable).
8. **Quality scoring** — if `quality-overview.md` exists, verify it contains:
   - A scoring rubric (Grade | Criteria table)
   - A weighted calculation reference
   Report as WARNING if missing.

Append issues to tracking lists.

**After each batch:**
```
Validated batch {n}: {file1}, {file2}, ... — {issues_found} issues
```

### Phase 3: Cross-Batch Checks

1. Verify index files (api-index, adr-index) link to their child pages
2. Verify overview files link to detail pages
3. **Paired file duplication check** — for these file pairs, flag if the same paragraph (>30 words) appears in both:
   - `testing-overview.md` ↔ `testing-strategy.md`
   - `quality-overview.md` ↔ `quality-recommendations.md`
   Report as WARNING if significant duplication found.

### Phase 4: Report

Display:
```
Markdown Validation Report
==========================
Files: {actual}/{expected} generated
Wave plan: {OK or issue description}
Frontmatter: {issue_count} issues
Mermaid diagrams: {issue_count} issues
Legacy markers: {issue_count} issues
Cross-references: {issue_count} issues
Content quality: {issue_count} issues
Structure (Source Files, tables): {issue_count} issues

{List each issue with filename, severity, and description}

Overall: PASS/FAIL
```

**Severity rules:**
- CRITICAL: legacy markers, missing expected files → automatic FAIL
- WARNING: missing Source Files section, missing scoring rubric, content duplication, broken cross-refs → FAIL if > 5 warnings
- INFO: missing table totals/percentages → does not affect pass/fail

Write to `docs/.validation-md-report.json`:
```json
{
  "generated": "date",
  "total_files": N,
  "expected_files": N,
  "issues": [{"severity":"critical|warning|info", "file":"...", "check":"...", "message":"..."}],
  "passed": true/false
}
```

### Rules
- Read files in batches of 5 — never more
- Every file must be read and checked — no skipping
- Legacy `<!-- diagram-meta` or `<!-- diagram:` markers = CRITICAL (indicates unconverted skill output)
- Missing plan files = CRITICAL issue
- After each batch, rely on issue lists, not file content
- Be specific in issue descriptions — include the line number or section name where the problem was found

## Tools
- Glob, Read, Write
