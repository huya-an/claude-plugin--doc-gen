# doc-quality

## Description
Generates code quality documentation: static analysis assessment, dependency health, tech debt inventory with quantified counts, and prioritized recommendations with acceptance criteria and verification steps. Runs as Wave 4 — synthesizes findings from all prior waves into cross-domain quality assessment with a defined scoring rubric. Produces a quality dashboard with letter grades and an actionable recommendation backlog.

## Context
fork

## References
- ../references/mermaid-diagram-guide.md

## Instructions

### Inputs
1. Read `docs/.doc-plan.json` — verify `doc-quality` is enabled
2. Read `docs/.doc-manifest.json` — get files under `doc-quality.files`
3. Read assigned source files in batches of 5-8 to stay within context limits
4. Read prior wave output for complete system context (do not regenerate):
   - Wave 1: `docs/md/arch-overview.md` (system overview, tech stack, risks table), `docs/md/arch-c4-level2.md` (container diagram)
   - Wave 2: `docs/md/api-index.md`, `docs/md/data-overview.md`, `docs/md/events-overview.md` (read whichever exist)
   - Wave 3: `docs/md/security-overview.md` (security posture), `docs/md/devops-overview.md` (CI/CD pipeline), `docs/md/testing-overview.md` (testing strategy and coverage)
   Use these to synthesize cross-domain recommendations. For example: "add integration tests for the payment endpoint's DynamoDB writes" requires knowing the API surface (Wave 2), data access patterns (Wave 2), and testing gaps (Wave 3).
5. Read `mermaid-diagram-guide.md` from the shared references directory for Mermaid syntax

### Analysis Steps
1. **Static analysis tools** — identify configured tools: linters (ESLint, Pylint, Flake8, RuboCop, Checkstyle, PMD, SpotBugs, clippy), formatters (Prettier, Black, gofmt, rustfmt), type checkers (TypeScript strict, mypy, Sorbet), security scanners (Snyk, OWASP Dep Check, Trivy, Bandit, cargo-audit), quality platforms (SonarQube, CodeClimate). Document: which are configured, which run in CI, which have enforced thresholds.
2. **Dependency analysis** — from build/package files: count direct vs transitive deps, flag outdated/deprecated packages, check for duplicates/conflicts, note management strategy (pinned, ranges, lockfiles). Check for known vulnerabilities if advisory databases are referenced in config.
3. **Code pattern assessment** — assess: style/pattern consistency, error handling patterns, logging practices, config management approach, dead code indicators (unused imports, commented-out code).
4. **Tech debt indicators** — search for: TODO/FIXME/HACK/XXX comments (exact count via Grep), suppressed warnings (@SuppressWarnings, eslint-disable, #[allow()], # type: ignore), deprecated API usage, large files (by line count), deep nesting. Count PRECISELY — use Grep results, not estimates. Never use approximate numbers (no `~138` — count exactly).
5. **Cross-domain synthesis** — using prior wave output, identify quality concerns that span domains:
   - Untested critical paths (cross-ref testing-overview.md endpoint coverage with api-index.md)
   - Security gaps affecting code quality (cross-ref security-overview.md)
   - Infrastructure risks affecting reliability (cross-ref devops-overview.md)
   - Architectural risks from arch-overview.md that manifest as code quality issues

### Output Files
All files go to `docs/md/`.

The two files have distinct purposes — **do not duplicate content between them**:
- **quality-overview.md** = Diagnostic dashboard — what was observed, with data. No recommendations here.
- **quality-recommendations.md** = Prescriptive backlog — what to fix, how, and how to verify. Each finding gets a 1-sentence summary linking to the overview, not a re-description.

#### `quality-overview.md` — Quality Dashboard

Frontmatter: title "Code Quality Overview", section "Quality", order 1, generated "{{DATE}}".

Content structure:

**1. Quality Score** — ALWAYS the first section (executive summary):

```markdown
## Quality Score: C+

| Dimension | Grade | Rationale |
|-----------|-------|-----------|
| Static Analysis Tooling | D | No linters or formatters configured |
| Dependency Health | B- | 48 deps, no known vulnerabilities, 3 outdated |
| Error Handling | B | Consistent pattern with custom exceptions, 1 silent catch |
| Test Coverage | C | JaCoCo configured but no enforced thresholds |
| Code Hygiene | C+ | 28 ObjectMapper instantiations, 4 debug prints |
| Logging & Observability | B+ | Structured logging via @Slf4j, 599 calls, no manual loggers |
```

**Scoring Rubric** — apply this rubric consistently. Include it as a collapsed/summary section or footnote so readers understand the criteria:

| Grade | Criteria |
|-------|----------|
| **A** | Tool configured, enforced in CI with thresholds, thresholds met, best practices followed |
| **B** | Tool configured and running in CI, minor gaps (no thresholds, or thresholds not fully met) |
| **C** | Tool exists or pattern is present, but not enforced in CI, or significant gaps |
| **D** | Not configured / not present, relying on manual discipline |
| **F** | Actively harmful patterns (e.g., security scanners disabled, unsafe code without justification) |

Use +/- modifiers within each grade. The **overall score** is a weighted synthesis:
- Static Analysis Tooling: 20%
- Dependency Health: 15%
- Error Handling: 20%
- Test Coverage: 20%
- Code Hygiene: 15%
- Logging & Observability: 10%

State the weighted calculation explicitly so the grade is reproducible.

**2. Quality Toolchain** — table with standardized columns:

| Tool | Category | Status | CI Enforced | Config File |
|------|----------|--------|-------------|-------------|
| clippy | Linter | Configured | Yes | CI pipeline |
| cargo fmt | Formatter | Configured | Yes (check mode) | CI pipeline |
| cargo-audit | Security | Not configured | — | — |
| JaCoCo | Coverage | Configured | No thresholds | pom.xml |

**Status** values: `Configured`, `Not configured`, `Configured but disabled`
**CI Enforced** values: `Yes`, `Yes (check mode)`, `No`, `—`

Also include a **Missing Tools** callout: list the tools that would be expected for this language/framework but are absent. For Java: Checkstyle/SpotBugs/PMD. For Rust: cargo-audit/cargo-tarpaulin/cargo-deny. For JS/TS: ESLint/Prettier/TypeScript strict mode.

**3. Dependency Summary:**

| Metric | Value |
|--------|-------|
| Direct dependencies | 35 |
| Test dependencies | 6 |
| Total (incl. transitive) | 487 |
| Outdated | 4 |
| Deprecated | 1 (Springfox) |
| Known vulnerabilities | 0 (not scanned) / 3 (from audit) |
| Duplicate versions | 2 (AWS SDK v1 + v2) |
| Management strategy | BOM + version pinning |

If no vulnerability scanning is configured, state: "Known vulnerabilities: **Not scanned** — no security audit tool configured."

**4. Tech Debt Inventory** — exact counts from Grep with severity:

| Indicator | Count | Severity | Files |
|-----------|-------|----------|-------|
| TODO/FIXME comments | 3 | Low | app_config.rs:42, database.rs:88, trip_service.rs:201 |
| Suppressed warnings | 16 (6 prod / 10 test) | Medium | Listed below |
| Silent exception catches | 1 | High | VehicleService.java:234 |
| Debug/print statements | 4 | Medium | Listed below |
| Anti-pattern instances | 28 (new ObjectMapper()) | High | Listed below |
| Large files (>500 lines) | 6 | Medium | Listed below |

**Severity assignment rules** — do NOT assign the same severity to everything:
- **High**: Patterns that can cause production bugs or security issues (silent catches, unhandled errors, unsafe code, hardcoded secrets)
- **Medium**: Patterns that degrade maintainability (suppressed warnings in production code, debug prints, large files, anti-patterns)
- **Low**: Minor hygiene issues (TODOs, test-only suppressions, minor style inconsistencies)

For indicators with >5 instances, list the top 5 files by occurrence count. For the rest, provide file paths in a sub-table.

**5. Code Pattern Assessment:**

Organize as two subsections:
- **Positive Patterns** — what the codebase does well (consistent error handling, structured logging, etc.). Each item: 1 sentence + evidence.
- **Concerns** — patterns that need attention. Each item: 1 sentence + quantified evidence + link to relevant recommendation.

Every concern listed here MUST have a corresponding recommendation in `quality-recommendations.md`. Do not identify problems without proposing solutions.

**6. Cross-Domain Findings** — quality issues that emerge from cross-referencing prior wave output:

| Finding | Source | Impact | Recommendation |
|---------|--------|--------|---------------|
| 8 API endpoints have no test coverage | testing-overview.md × api-index.md | Untested critical paths | See R-H2 |
| Dual AWS SDK creates dependency confusion | arch-overview.md risks table | Maintenance burden | See R-M3 |
| No security scanning despite external API calls | security-overview.md × quality toolchain | Undetected vulnerabilities | See R-C1 |

This section is the key value-add of being a Wave 4 agent — **only possible because all prior waves have completed**.

**7. Links** — to quality-recommendations.md and relevant prior wave docs.

#### `quality-recommendations.md` — Actionable Backlog

Frontmatter: title "Quality Recommendations", section "Quality", order 2, generated "{{DATE}}".

Content structure:

**1. Quick-Win Actions** — ALWAYS start with this (3-5 items a developer can do in <1 day):

```markdown
## Quick-Win Actions

Start here. These are the highest-impact changes that can be completed quickly:

1. **Fix BOM declarations** (1h) — move 3 BOMs from `<dependencies>` to `<dependencyManagement>`. See R-C1.
2. **Add cargo-audit to CI** (30min) — one YAML line addition. See R-C2.
3. **Remove debug prints** (30min) — replace 4 System.out.println calls with proper logging. See R-H3.
4. **Pin floating dependency** (15min) — lock ConfigCat version. See R-M4.
```

**2. Recommendation Backlog** — organized by priority tier with coded IDs:

Use the format `R-{TIER}{NUMBER}` for IDs: R-C1 (Critical #1), R-H1 (High #1), R-M1 (Medium #1), R-L1 (Low #1).

Each recommendation follows this structure:

```markdown
### R-C1: Fix BOM Dependency Declarations

**Severity:** Critical | **Effort:** 1 hour | **Dimension:** Dependency Health

**Problem:** 3 BOMs are declared in `<dependencies>` instead of `<dependencyManagement>`, causing version conflicts. (See quality-overview.md § Tech Debt Inventory)

**Recommendation:** Move the following BOMs to `<dependencyManagement>`:
- `spring-cloud-dependencies` (pom.xml:45)
- `aws-sdk-bom` (pom.xml:52)
- `testcontainers-bom` (pom.xml:61)

**Before:**
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-dependencies</artifactId>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencies>
```

**After:**
```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

**Acceptance criteria:**
- `mvn validate` passes with zero BOM warnings
- No dependency version conflicts in `mvn dependency:tree`

**Verification:** Run `mvn validate 2>&1 | grep -i "bom"` — should produce no output.

**Relevant files:** pom.xml
```

**MANDATORY fields per recommendation:**
- Severity (Critical / High / Medium / Low)
- Effort estimate (specific: "1 hour", "2-3 hours", "1 day", not "1-2 weeks" for a batch)
- Dimension (which quality score dimension this improves)
- Problem (1-2 sentences, linking to overview — do NOT re-describe the full finding)
- Recommendation (specific action with file paths)
- Before/after code (when applicable — at least for Critical and High items)
- Acceptance criteria (what "done" looks like)
- Verification (command to run to confirm the fix)
- Relevant files

**Priority tiers:**
- **Critical (R-C)**: Issues that can cause build failures, runtime errors, or security vulnerabilities. Fix this sprint.
- **High (R-H)**: Issues that significantly degrade maintainability or developer experience. Fix this quarter.
- **Medium (R-M)**: Improvements that would noticeably improve code quality. Schedule when bandwidth allows.
- **Low (R-L)**: Polish items. Address opportunistically during related changes.

**3. Dependency Updates** — integrated into the priority tiers (not a separate section). Each outdated/deprecated dependency gets its own recommendation with the standard structure. Deprecated libraries are High priority; outdated-but-functional are Medium or Low.

**4. Impact Summary** — table at the end showing what the quality score would become if all recommendations were implemented:

| Dimension | Current | After Critical | After All |
|-----------|---------|---------------|-----------|
| Static Analysis Tooling | D | D | B+ |
| Dependency Health | B- | B | A- |
| Error Handling | B | B | A- |
| Test Coverage | C | C | B |
| Code Hygiene | C+ | B- | A- |
| Logging & Observability | B+ | B+ | A |
| **Overall** | **C+** | **B-** | **B+** |

This shows stakeholders the ROI of investing in quality improvements.

**5. Source Files** — list the key files analyzed.

### Rules
- TODO/FIXME/indicator counts must be EXACT — from actual Grep results, never estimates. No `~` approximate counts.
- Dependency counts must be from actual build/package files
- Every quality score must follow the defined rubric with weighted calculation
- Every concern in the overview MUST have a corresponding recommendation
- Every recommendation MUST have acceptance criteria and a verification step
- **No content duplication between overview and recommendations** — findings live in overview, fixes live in recommendations. Recommendations get a 1-sentence problem summary linking to the overview section.
- Severity labels must be distinct and meaningful — do NOT assign the same severity to most items
- Reference specific files and line numbers for every finding
- Be objective — document what IS, not what you think SHOULD be. Clearly distinguish facts (configs found, counts measured) from assessments (quality judgment via rubric)
- **Source files**: at the end of each page, include a `## Source Files` section listing the key files analyzed

## Tools
- Read
- Glob
- Grep
- Write

## Output
Markdown files in `docs/md/`:
- `quality-overview.md`
- `quality-recommendations.md`
