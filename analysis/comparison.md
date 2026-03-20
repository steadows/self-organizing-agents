# Score Comparison — Baseline vs Evolved Rounds

## Overall Trajectory

| Stage | Rules | Mean Score | Δ vs Baseline | Δ vs Previous | Acceptance |
|-------|-------|-----------|---------------|---------------|------------|
| Baseline | v0 | 8.00 | — | — | 5/5 |
| Round 01 | v0 | 9.32 | +1.32 | +1.32 | 5/5 |
| Round 02 | v1 | 9.56 | +1.56 | +0.24 | 5/5 |
| Round 03 | v2 | 9.58 | +1.58 | +0.02 | 5/5 |

**Total improvement:** +1.58 points (19.8% relative gain)
**Acceptance tests:** 100% pass rate across all rounds (20/20 task-round combinations)

## Per-Task Trajectories

| Task | Baseline | R1 (v0) | R2 (v1) | R3 (v2) | Total Δ |
|------|----------|---------|---------|---------|---------|
| task-001 (slugify) | 7.7 | 9.0 | 9.7 | 9.3 | +1.6 |
| task-002 (validate_email) | 8.2 | 9.3 | 9.3 | 9.3 | +1.1 |
| task-003 (safe_write) | 7.8 | 9.3 | 9.8 | 9.8 | +2.0 |
| task-004 (retry_with_backoff) | 8.3 | 9.5 | 9.5 | 9.8 | +1.5 |
| task-005 (ttl_cache) | 8.2 | 9.5 | 9.5 | 9.7 | +1.5 |

### Notable Patterns

- **task-003 (safe_write)** saw the largest total improvement (+2.0), going from the second-lowest baseline to tied-highest in rounds 2-3.
- **task-001 (slugify)** is the only task that regressed between rounds (9.7 → 9.3 from R2 to R3), suggesting the evolved rules may have introduced trade-offs for this task type.
- **task-002 (validate_email)** plateaued at 9.3 from round 1 onward — the rules had minimal effect on this task after the initial execution improvement.

## Per-Dimension Analysis (Round 03 vs Baseline)

| Dimension | Baseline Avg | Round 03 Avg | Δ |
|-----------|-------------|-------------|---|
| Correctness | 8.4 | 10.0 | +1.6 |
| Edge Cases | 8.4 | 10.0 | +1.6 |
| Code Quality | 8.0 | 9.2 | +1.2 |
| Documentation | 8.0 | 9.8 | +1.8 |
| Test Coverage | 8.2 | 9.6 | +1.4 |
| Robustness | 7.2 | 9.0 | +1.8 |

### Dimension Insights

- **Correctness and Edge Cases** reached perfect 10.0 — the ceiling effect means further rule evolution cannot improve these dimensions.
- **Robustness** showed the largest absolute gain (+1.8), rising from the weakest baseline dimension (7.2) to 9.0. This directly maps to the Round 01 rule changes: parameter validation guards and failure-path mock tests.
- **Documentation** also gained +1.8, corresponding to the `Examples:` section requirement added in Round 01 and helper docstring guidance in Round 02.
- **Code Quality** improved least (+1.2), suggesting that style/structure improvements are harder to prescribe via rules than correctness or documentation patterns.

## Interpretation

The majority of improvement (+1.32 of +1.58) came from Round 01 — the first application of any evolved rules (even though R1 still used v0 rules, it benefited from being a second execution attempt). Subsequent rounds showed diminishing returns:

- R1→R2: +0.24 (v0→v1 rules applied)
- R2→R3: +0.02 (v1→v2 rules applied)

This logarithmic convergence is expected. The easy gains (documentation examples, parameter validation, failure-path tests) were captured in Round 01's consolidation. Round 02's changes (helper docstrings, precise generics) were more niche, yielding smaller marginal improvements. The system is approaching the quality ceiling for these task types and this judge rubric.
