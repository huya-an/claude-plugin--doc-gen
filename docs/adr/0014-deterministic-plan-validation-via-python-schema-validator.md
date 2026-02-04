# ADR-0014: Deterministic Plan Validation via Python Schema Validator

## Status
Accepted

## Date
2026-02-01

## Context

The `/doc` discovery command produces a `.doc-plan.json` file that drives all downstream generation. The plan JSON must conform to a strict schema — every section needs required fields (`id`, `title`, `description`, `files`, `priority`, `estimatedPages`), and the `priority` field must use wave-based values (`wave-1` through `wave-4`) per ADR-0010.

During testing, the LLM-generated plan JSON repeatedly failed schema compliance despite explicit instructions in `doc-discover/SKILL.md`:

- `priority` values were generated as `high`/`medium`/`low` instead of `wave-1`/`wave-2`/`wave-3`/`wave-4`
- Required fields were intermittently omitted
- The `files` array sometimes contained glob patterns instead of concrete file paths

Adding more emphatic language to the skill prompt ("MUST use wave-N format", "NEVER use high/medium/low") reduced but did not eliminate violations. LLM prompt compliance for structured output is inherently probabilistic — no amount of prompt engineering guarantees 100% conformance.

## Decision

Introduce a zero-dependency Python schema validator (`validate-plan.py`) that runs as a blocking validation step after plan generation. If validation fails, the discovery agent must fix violations and re-validate in a loop until the plan passes.

### Validator: `doc-discover/references/validate-plan.py`

```
Usage: python3 validate-plan.py <plan.json>
Exit 0: valid, prints "VALID"
Exit 1: invalid, prints each violation on a separate line
```

Validates:
- Top-level structure has `projectName`, `sections` array, `generatedAt`
- Each section has all required fields with correct types
- `priority` is one of `wave-1`, `wave-2`, `wave-3`, `wave-4`
- `files` is a non-empty array of strings
- `estimatedPages` is a positive integer
- No duplicate section IDs

### Validation loop in discovery flow

Both `doc-discover/SKILL.md` (Step 7) and `doc.md` command (Step 3f) include a mandatory validation loop:

```
Run: python3 references/validate-plan.py docs/.doc-plan.json
If exit code != 0:
  Read the violation messages
  Fix each violation in the plan JSON
  Re-run validation
  Repeat until exit code == 0
```

The validator is deterministic — same input always produces same output. This converts "LLM might not follow the prompt" into "LLM must fix its output until a machine check passes."

## Consequences

### Positive
- Plan JSON is guaranteed schema-compliant before any downstream agent reads it
- Eliminates an entire class of silent failures (wrong priority values causing incorrect wave assignment, missing fields causing agent crashes)
- Zero-dependency: uses only Python standard library (`json`, `sys`), available on every system with Python 3
- Validation errors are specific and actionable — the LLM can read them and fix exactly what's wrong
- The loop pattern is self-healing: even if the first attempt has violations, the agent converges to a valid plan within 1-2 iterations

### Negative
- Adds one extra tool call (Bash) per discovery run, plus additional calls if validation fails
- The validation loop could theoretically not terminate if the LLM keeps introducing new violations while fixing old ones. In practice this has not occurred — violations are independent and the error messages are unambiguous.
- Schema changes require updating both the validator and the skill prompt, creating a dual-maintenance burden

### Follow-up Actions
- Consider extending the pattern to validate other generated artifacts (`.doc-manifest.json`, `.site-manifest.json`)
- Review this decision on: 2026-03-01

## Alternatives Considered

### 1. Stronger prompt engineering only
- Rejected: Tested extensively. Even with capitalized warnings, examples, and negative examples, the LLM intermittently generated `high`/`medium`/`low` instead of `wave-N`. Prompt compliance is probabilistic; validation is deterministic.

### 2. JSON Schema validation via `jsonschema` Python package
- Rejected: Requires `pip install jsonschema`, adding a dependency that may not be available in the user's environment. The validation rules are simple enough that a 60-line script with `json` and `sys` covers all cases.

### 3. Post-hoc correction (fix plan after generation without re-validation)
- Rejected: A single-pass correction might introduce its own errors. The loop pattern guarantees convergence by re-checking after every fix attempt.

### 4. TypeScript/Node.js validator
- Rejected: Python is more universally available than Node.js across development environments. The plugin targets any codebase (Java, Python, Go, etc.), not just JavaScript projects.

## References
- ADR-0010: Wave-Based Execution Ordering
- `plugins/doc-gen/skills/doc-discover/references/validate-plan.py`
- `plugins/doc-gen/skills/doc-discover/SKILL.md` — Step 7
- `plugins/doc-gen/commands/doc.md` — Step 3f
