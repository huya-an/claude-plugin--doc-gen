# doc-data

## Description
**DEPRECATED** — This skill has been split into 4 focused sub-skills to stay within forked agent context limits:

| Sub-Skill | Wave | Purpose |
|---|---|---|
| `doc-data-discover` | 2 | Lightweight scanner — Glob/Grep only, produces `.data-manifest.json` |
| `doc-data-tables` | 3 | One page per table with 6-category DBA scorecard |
| `doc-data-queries` | 4 | One page per query with 5-category DBA scorecard |
| `doc-data-overview` | 5 | Rollup overviews, ERDs, data pipelines |

Use the sub-skills instead. The plan template and doc-generate command reference the sub-skill IDs (`doc-data-discover`, `doc-data-tables`, `doc-data-queries`, `doc-data-overview`), not `doc-data`.
