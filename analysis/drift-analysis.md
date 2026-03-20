# Behavioral Drift Analysis — Rules v0 → v1 → v2

## Summary

Over 2 consolidation rounds, the rule system grew from 65 lines (v0) to 71 lines (v2) — a modest 9.2% increase. All changes were additive (new guidance). No existing rules were removed, contradicted, or restructured.

## Rule File Growth

| File | v0 Lines | v1 Lines | v2 Lines | Growth |
|------|----------|----------|----------|--------|
| code-quality.md | 19 | 21 | 23 | +4 (+21%) |
| output-format.md | 21 | 21 | 21 | 0 (0%) |
| task-executor.md | 25 | 27 | 27 | +2 (+8%) |
| **Total** | **65** | **69** | **71** | **+6 (+9.2%)** |

All files remain well under the 150-line cap. No file exceeds 27 lines.

## Change Inventory

### Round 01: v0 → v1 (4 changes accepted, 1 rejected)

| # | File | Type | Description | Attribution |
|---|------|------|-------------|-------------|
| 1 | code-quality.md | ADD | Dead code audit: "verify every assigned variable and import is referenced; remove unused" | Critique 1 |
| 2 | code-quality.md | MODIFY | Documentation `Examples:` section requirement added | Critique 2 |
| 3 | task-executor.md | ADD | Parameter validation for spec-constrained values (ValueError guard) | Critique 3 (modified by Defender) |
| 4 | task-executor.md | MODIFY | Failure-path mock tests for I/O functions | Critique 4 (modified by Defender) |
| — | *(rejected)* | — | Helper function docstrings — weak evidence | Critique 5 (rejected) |

### Round 02: v1 → v2 (2 changes accepted, 3 rejected)

| # | File | Type | Description | Attribution |
|---|------|------|-------------|-------------|
| 1 | code-quality.md | MODIFY | Tiered helper docstrings: one-line minimum, full params when complex | Critique 2 |
| 2 | code-quality.md | MODIFY | Precise generic type hints: parameterized tuple/Callable | Critique 3 |
| — | *(rejected)* | — | Regex pre-compilation — over-specification | Critique 1 (rejected) |
| — | *(rejected)* | — | Input type validation (isinstance) — duck-typing risk | Critique 4 (rejected) |
| — | *(rejected)* | — | Unused parameters — single-task, spec-driven | Critique 5 (rejected) |

## Change Categories

| Category | Count | Examples |
|----------|-------|---------|
| New guidance (ADD) | 2 | Dead code audit, parameter validation |
| Clarification (MODIFY) | 4 | Examples in docs, failure-path tests, helper docstrings, generic types |
| Removal | 0 | — |
| Restructuring | 0 | — |

All 6 accepted changes are clarifications or additions to existing rules. The consolidation loop never removed or restructured guidance — it only added precision.

## Rejection Analysis

| Round | Proposed | Accepted | Rejected | Rejection Rate |
|-------|----------|----------|----------|----------------|
| 1 | 5 | 4 | 1 | 20% |
| 2 | 5 | 2 | 3 | 60% |

The increasing rejection rate from Round 1 (20%) to Round 2 (60%) reflects:
1. **Diminishing returns:** Early critiques addressed broad patterns (5/5 tasks affected). Later critiques were often single-task observations.
2. **Defender effectiveness:** The Defender agent successfully filtered over-specifications (regex pre-compilation, isinstance checks) that could have caused regressions.
3. **Human alignment:** The human approver's rejections matched the Defender's in all cases — no conflict between agent and human judgment.

## Bloat Assessment

| Metric | Value | Assessment |
|--------|-------|------------|
| Total line growth | +6 lines | Minimal |
| Growth rate | +3 lines/round | Sustainable for 10+ rounds |
| Max file size | 27 lines (v2 task-executor.md) | 18% of 150-line cap |
| Rules contradictions | 0 | Clean |
| Rules removed | 0 | No churn |

**No bloat detected.** The consolidation loop's constraints (20-line cap per file per round, Defender filtering, human approval) successfully prevented rule inflation. At the current growth rate, it would take ~40 rounds to approach the 150-line cap on any file.

## Attribution Coverage

All 6 accepted changes carry `<!-- addresses: Critique N -->` attribution labels in the proposal files. Both approval records (`consolidation/approvals/round-01.md`, `round-02.md`) include per-change rationales.

## Drift Direction

The rules drifted exclusively toward **more precision**, not more scope:
- v0: "Handle basic error cases" → v1: adds specific guidance on which parameters to validate
- v0: "Describe parameters and return values" → v1: adds Examples section → v2: extends to helper functions
- v0: "Add type hints" → v2: adds precision requirements on generic types

No rules expanded to cover new topics. All evolution stayed within the original rule domains (code quality, documentation, testing, implementation).
