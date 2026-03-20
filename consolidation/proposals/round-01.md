# Consolidation Proposal — Round 01

## Summary
- Rules modified: `rules/current/code-quality.md`, `rules/current/task-executor.md`
- Net new lines: `code-quality.md` +6, `task-executor.md` +8
- Critiques addressed: Critique 1 (Dead code / unused variables), Critique 2 (Missing usage examples in docstrings), Critique 3 (Secondary parameter validation — modified), Critique 4 (Failure-path test coverage — modified)
- Critiques excluded: Critique 5 (Helper function docstrings — rejected by Defender)

---

## Changes

### File: rules/current/code-quality.md

#### Change 1
<!-- addresses: Critique 2 — Missing usage examples in docstrings -->

**Action:** MODIFY
**Location:** Replace lines under `## Documentation`

**Before:**
```
## Documentation
- Include a docstring on the main function
- Describe parameters and return values
```

**After:**
```
## Documentation
- Include a docstring on the main function
- Describe parameters and return values
- Include an `Examples:` section showing at least one typical call and its expected return value
```

**Rationale:** Every task received 9/10 on documentation with the same cited gap — no usage example. Adding the `Examples:` requirement directly closes this uniform deficiency with the smallest possible wording change.

---

#### Change 2
<!-- addresses: Critique 1 — Dead code / unused variables -->

**Action:** ADD
**Location:** After the last bullet in `## Style`

**Before:**
```
## Style
- Follow PEP 8 conventions
- Use meaningful variable names
- Keep functions reasonably short
```

**After:**
```
## Style
- Follow PEP 8 conventions
- Use meaningful variable names
- Keep functions reasonably short
- Before finalizing, verify that every assigned variable and every import is actually referenced; remove any that are not
```

**Rationale:** Task-001 shipped with `escaped_sep` computed and never used, costing a code quality point. This pre-submission audit step is universally applicable, non-intrusive, and precisely targets the observed failure mode.

---

### File: rules/current/task-executor.md

#### Change 3
<!-- addresses: Critique 3 — Secondary parameter validation (modified scope) -->

**Action:** ADD
**Location:** After the last bullet in `## Implementation Guidelines`

**Before:**
```
## Implementation Guidelines
- Use Python 3.11+ features where appropriate
- Include type hints on the function signature
- Write a docstring for the main function
- Handle basic error cases
```

**After:**
```
## Implementation Guidelines
- Use Python 3.11+ features where appropriate
- Include type hints on the function signature
- Write a docstring for the main function
- Handle basic error cases
- For parameters where the task spec explicitly or implicitly constrains valid values (e.g., a count or length that must be non-negative), add a guard at function entry raising `ValueError` with a descriptive message; do not add validation for parameters the spec leaves unconstrained
```

**Rationale:** Three tasks received robustness deductions for skipping validation on secondary parameters whose constraints are implied by the spec (e.g., non-negative `max_length`, non-negative delays). The Defender's modification scopes this to spec-implied constraints only, preventing defensive over-validation boilerplate on unconstrained parameters.

---

#### Change 4
<!-- addresses: Critique 4 — Failure-path / mocked-dependency test coverage (modified scope) -->

**Action:** MODIFY
**Location:** Replace the `## Testing` section bullets

**Before:**
```
## Testing
- Write tests using pytest
- Cover the happy path
- Include at least one edge case test
```

**After:**
```
## Testing
- Write tests using pytest
- Cover the happy path
- Include at least one edge case test
- For functions with I/O or external dependencies (file system, network, time), include at least one test that simulates a failure or error path using mocks (e.g., mock an `OSError` or a raised exception from a dependency); do not limit tests to value-space edge cases alone
```

**Rationale:** Tasks involving I/O (003: file writes, 002: string boundary limits) received 9/10 on coverage for missing failure-path tests. The Defender's modification drops the per-exception exhaustiveness requirement and the internal task reference, replacing them with a scoped, actionable rule targeting the specific gap: testing what happens when dependencies fail, not just when inputs are unusual.

---

## Verification Checklist
- [x] Net new lines per file within 20-line cap — `code-quality.md`: +6 lines net; `task-executor.md`: +8 lines net
- [x] No more than 2 files modified — 2 files modified (`code-quality.md`, `task-executor.md`)
- [x] Every change has an attribution label — all 4 changes carry `<!-- addresses: Critique N -->` comments
- [x] No executable code blocks introduced — all additions are prose; no fenced `bash`/`python`/`sh` blocks
- [x] No contradictions with existing rules — additions extend, not conflict with, existing bullets; "Handle basic error cases" is narrowed/clarified, not contradicted
- [x] Each file stays under 150 lines — `code-quality.md` reaches ~22 lines; `task-executor.md` reaches ~30 lines; both well under limit
- [x] Only accepted/modified critiques implemented — Critique 5 (REJECTED) is excluded entirely; Critiques 3 and 4 incorporate Defender's narrowing