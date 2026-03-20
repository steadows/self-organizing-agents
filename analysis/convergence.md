# Convergence Analysis

## Do per-round averages improve monotonically?

**Yes — overall means improve monotonically across all rounds.**

| Round | Mean Score | Δ from Previous |
|-------|-----------|-----------------|
| Baseline | 8.00 | — |
| Round 01 | 9.32 | +1.32 |
| Round 02 | 9.56 | +0.24 |
| Round 03 | 9.58 | +0.02 |

The trajectory is monotonically increasing but with sharply diminishing marginal returns.

## Does Round 3 plateau vs Round 2?

**Effectively yes.** The R2→R3 delta of +0.02 is within the noise floor of LLM scoring (judge temperature = 0.0, but prompt sensitivity remains). For practical purposes, the system converged by Round 2.

### Convergence curve shape

```
Score
10.0 |                                              ·····  (ceiling)
 9.5 |                    ●─────────●─────────●
 9.0 |          ●
 8.5 |
 8.0 | ●
 7.5 |
     +────────────────────────────────────────────
       Baseline    R1        R2        R3
```

The curve exhibits classic diminishing returns — a large initial jump followed by asymptotic approach to a ceiling. This is consistent with:
1. **Easy wins first:** The consolidation loop captures broad, high-impact patterns in Round 01.
2. **Ceiling effect:** Correctness and edge cases hit 10.0 by Round 03, leaving no room for further improvement.
3. **Diminishing critique quality:** Round 02's critic found fewer universal patterns (3 of 5 critiques rejected vs 1 of 5 in Round 01).

## Which dimensions converge fastest?

| Dimension | Baseline | R3 | Δ | Rounds to 10.0 |
|-----------|---------|-----|---|-----------------|
| Correctness | 8.4 | 10.0 | +1.6 | 3 (converged) |
| Edge Cases | 8.4 | 10.0 | +1.6 | 3 (converged) |
| Documentation | 8.0 | 9.8 | +1.8 | >3 (near ceiling) |
| Test Coverage | 8.2 | 9.6 | +1.4 | >3 (approaching) |
| Code Quality | 8.0 | 9.2 | +1.2 | >3 (slowest) |
| Robustness | 7.2 | 9.0 | +1.8 | >3 (most improved but not converged) |

**Fastest to converge:** Correctness and Edge Cases (perfect 10.0 by R3).
**Slowest to converge:** Code Quality (9.2) and Robustness (9.0) — subjective dimensions where rules have less direct leverage.

### Interpretation

Dimensions with clear, testable criteria (correctness, edge cases) converge fastest because:
- The rules can prescribe specific actions (parameter validation, failure-path tests)
- The acceptance test suite provides ground-truth feedback
- The judge can objectively verify compliance

Dimensions involving judgment (code quality, robustness) converge slower because:
- Improvement requires nuanced stylistic changes that are harder to encode in rules
- The rules can only prescribe patterns ("verify imports are used") rather than taste
- These dimensions have inherently more variance in scoring

## Do any tasks resist improvement?

| Task | Baseline | Best Score | Improvement | Pattern |
|------|----------|-----------|-------------|---------|
| task-001 (slugify) | 7.7 | 9.7 (R2) | +2.0 | Peaked at R2, regressed to 9.3 at R3 |
| task-002 (validate_email) | 8.2 | 9.3 (R1-R3) | +1.1 | Plateaued from R1 — least improved |
| task-003 (safe_write) | 7.8 | 9.8 (R2-R3) | +2.0 | Converged by R2 |
| task-004 (retry_with_backoff) | 8.3 | 9.8 (R3) | +1.5 | Steady improvement |
| task-005 (ttl_cache) | 8.2 | 9.7 (R3) | +1.5 | Steady improvement |

**task-002 (validate_email)** is the most improvement-resistant task, plateauing at 9.3 from Round 01 onward. This suggests its remaining quality gaps (likely in code quality or robustness dimensions) are not addressable by the types of rules the consolidation loop generates.

**task-001 (slugify)** is the only task that regressed between rounds (9.7 → 9.3 from R2 to R3). This is notable because R3 used v2 rules, which added precision requirements for type hints — potentially causing the executor to make different trade-offs.

## Do acceptance test pass rates correlate with judge scores?

**All tasks passed acceptance tests in all rounds (20/20 evolution, 6/6 holdout).** There is no variance in acceptance pass rates to correlate against judge scores.

This indicates:
1. The tasks are well-calibrated — Claude Opus can produce correct implementations reliably.
2. The judge scores capture quality dimensions beyond correctness (style, docs, robustness) that acceptance tests don't measure.
3. Future experiments may need harder tasks where acceptance test passage is not guaranteed, to create variance on the correctness axis.

## Convergence Predictions

If the experiment continued to Round 04:
- Expected overall mean: ~9.58-9.62 (minimal change)
- Expected new rule changes: 0-1 (most critiques would be rejected as over-specification)
- Expected rejection rate: >70%
- The system would effectively be at steady state

**The consolidation loop reached practical convergence in 2-3 rounds for this task complexity.**
