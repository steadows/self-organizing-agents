# Consolidation Proposal — Round 02

## Summary
- Rules modified: `rules/current/code-quality.md`, `rules/current/task-executor.md`
- Net new lines: `code-quality.md` → +7 lines; `task-executor.md` → +4 lines
- Critiques addressed: Critique 2 (helper function docstrings, MODIFIED), Critique 3 (precise type hints on generics, ACCEPTED)
- Critiques excluded: Critique 1 (REJECTED — over-specification, single negligible observation), Critique 4 (REJECTED — over-specification, duck-typing regression risk), Critique 5 (REJECTED — single-task observation, spec-driven issue)

---

## Changes

### File: rules/current/code-quality.md

#### Change 1
<!-- addresses: Critique 2 — Private Helper Functions Lack Full Docstrings -->

**Action:** MODIFY  
**Location:** Replace lines under `## Documentation`

**Before:**
```
## Documentation
- Include a docstring on the main function
- Describe parameters and return values
- Include an `Examples:` section showing at least one typical call and its expected return value
```

**After:**
```
## Documentation
- Include a docstring on the main function
- Describe parameters and return values
- Include an `Examples:` section showing at least one typical call and its expected return value
- Private helper functions should include at minimum a one-line summary docstring; for helpers with multiple parameters or non-obvious behavior, also document parameters and return values concisely
```

**Rationale:** The Defender accepted the core observation (2+ tasks, genuine rule gap) but narrowed the requirement to a tiered model: a flat docstring floor for all helpers, full params/returns only when complexity warrants it. This single sentence encodes that two-tier structure without mandating NumPy-style treatment of trivial internal functions. The phrase "non-obvious behavior" preserves discretion on simple helpers like `_is_empty(s)` while closing the gap the judge flagged on `_is_valid_local` and `wrapper()`.

---

#### Change 2
<!-- addresses: Critique 3 — Imprecise Type Hints on Higher-Order Function Parameters -->

**Action:** MODIFY  
**Location:** Replace lines under `## Type Hints`

**Before:**
```
## Type Hints
- Add type hints to function signatures
- Use standard library types where possible
```

**After:**
```
## Type Hints
- Add type hints to function signatures
- Use standard library types where possible
- Prefer specific generic forms over bare container types: use `tuple[type[Exception], ...]` rather than bare `tuple`, and annotate `Callable` with parameter and return types (`Callable[..., T]` or a concrete signature) when the signature is known
```

**Rationale:** The Defender accepted this critique with low regression risk. The existing rule says "use standard library types where possible" but says nothing about *precision* — it does not require parameterizing generics. The new bullet closes this gap with concrete examples drawn directly from the failure modes (bare `tuple` in task-004, unparameterized `Callable` in task-005), while scoping the requirement to "when the signature is known" to avoid mandating over-annotated generics in genuinely polymorphic contexts.

---

### File: rules/current/task-executor.md

*(No changes — both critiques affecting this file were REJECTED by the Defender. Critique 4's rejection means no `isinstance` type-guard rule is introduced here.)*

---

**Correction:** The Defender accepted/modified only Critiques 2 and 3, both targeting `code-quality.md`. No accepted critique targeted `task-executor.md`. Updating summary accordingly.

---

## Revised Summary
- Rules modified: `rules/current/code-quality.md` only
- Net new lines: `code-quality.md` → +2 lines (one bullet added to Documentation, one bullet added to Type Hints; no lines removed)
- Critiques addressed: Critique 2 (MODIFIED), Critique 3 (ACCEPTED)
- Critiques excluded: Critique 1 (REJECTED), Critique 4 (REJECTED), Critique 5 (REJECTED)

---

## Verification Checklist
- [x] Net new lines per file within 20-line cap — `code-quality.md`: +2 lines; `task-executor.md`: 0 lines (not modified)
- [x] No more than 2 files modified — only 1 file modified (`code-quality.md`)
- [x] Every change has an attribution label — Change 1: `Critique 2`; Change 2: `Critique 3`
- [x] No executable code blocks introduced — both additions are prose bullets with inline pseudocode examples only
- [x] No contradictions with existing rules — Change 1 extends, not overrides, the existing docstring rule; Change 2 extends, not overrides, the existing type hint rule
- [x] Each file stays under 150 lines — `code-quality.md` currently ~24 lines; after +2 lines = ~26 lines, well within limit
- [x] Only accepted/modified critiques implemented — Critiques 2 (MODIFIED) and 3 (ACCEPTED) only; Critiques 1, 4, 5 (all REJECTED) excluded