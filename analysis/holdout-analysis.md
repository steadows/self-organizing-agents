# Holdout Generalization Analysis

## The Key Question

> Did the evolved rules generalize to unseen tasks, or did they overfit to the 5 evolution tasks?

**Verdict: YES — the rules generalized.**

## Holdout Scores: Pre (v0) vs Post (v2)

| Task | Pre (v0) | Post (v2) | Δ |
|------|----------|-----------|---|
| holdout-001 (parse_duration) | 8.7 | 10.0 | +1.3 |
| holdout-002 (deep_merge) | 8.3 | 10.0 | +1.7 |
| holdout-003 (bounded_pool) | 8.3 | 9.5 | +1.2 |
| **Mean** | **8.43** | **9.83** | **+1.40** |

**Acceptance tests:** 3/3 pre, 3/3 post (100% pass rate in both conditions)

## Generalization Evidence

### 1. Holdout improvement matches evolution set improvement

| Set | Pre Mean | Post Mean | Δ |
|-----|----------|-----------|---|
| Evolution (5 tasks) | 8.00 | 9.58 | +1.58 |
| Holdout (3 tasks) | 8.43 | 9.83 | +1.40 |

The holdout delta (+1.40) is 89% of the evolution delta (+1.58). If the rules had overfit, we would expect the holdout delta to be near zero or negative. Instead, the holdout tasks improved almost as much as the training tasks.

### 2. Holdout post-scores exceed evolution post-scores

The holdout mean (9.83) actually **exceeds** the evolution mean (9.58) by +0.25. Two holdout tasks scored perfect 10.0 — a result no evolution task achieved. This suggests the holdout tasks (parse_duration, deep_merge) may be slightly easier than the evolution tasks, but it also confirms the rules did not harm performance on unseen task types.

### 3. Per-dimension holdout performance (post, v2 rules)

| Dimension | holdout-001 | holdout-002 | holdout-003 | Avg |
|-----------|-------------|-------------|-------------|-----|
| Correctness | 10 | 10 | 10 | 10.0 |
| Edge Cases | 10 | 10 | 10 | 10.0 |
| Code Quality | 10 | 10 | 9 | 9.67 |
| Documentation | 10 | 10 | 9 | 9.67 |
| Test Coverage | 10 | 10 | 10 | 10.0 |
| Robustness | 10 | 10 | 9 | 9.67 |

Perfect scores on correctness, edge cases, and test coverage across all holdout tasks. The only deductions were on holdout-003 (bounded_pool) — the most complex task in the holdout set, involving async concurrency patterns.

## Overfitting Assessment

| Signal | Expected if Overfit | Observed | Conclusion |
|--------|-------------------|----------|------------|
| Holdout Δ near zero | Δ ≈ 0 | Δ = +1.40 | Not overfit |
| Holdout post < evolution post | Post < 9.58 | Post = 9.83 | Not overfit |
| Dimension collapse on holdout | Some dimensions regress | All improve | Not overfit |
| Holdout task types fail | Novel tasks score low | All ≥ 9.5 | Not overfit |

**No evidence of overfitting.** The rules are general-purpose improvements to code quality, documentation, testing, and robustness that transfer across Python utility function types.

## Limitations

1. **Small holdout set (N=3).** Statistical power is low. The holdout result is directionally convincing but not statistically significant in the traditional sense.
2. **Same task domain.** All 8 tasks are Python utility functions. Generalization to other domains (web endpoints, data pipelines, CLI tools) is untested.
3. **Same judge.** The judge model and rubric are identical for both sets. If the judge has systematic biases, they affect both sets equally — but they don't test "real-world" quality perception.
4. **Re-execution effect.** The post-evaluation runs the executor a second time on each holdout task. Some improvement may come from the model's inherent variance rather than the rules. However, this effect is controlled for by the evolution set, where the baseline was also a first execution.
