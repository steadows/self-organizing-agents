# Cost Tracking

## Session Log Summary

**Total logged invocations:** 24
**Total tokens:** 260,279 input + 55,880 output = 316,159 total
**Total logged cost:** $1.24

### By Invocation Type

| Type | Count | Input Tokens | Output Tokens | Cost |
|------|-------|-------------|---------------|------|
| Judge (Sonnet 4.6) | 18 | 192,903 | 44,096 | $1.24 |
| Consolidation — Critic | 2 | 34,425 | 4,600 | ~$0.12* |
| Consolidation — Defender | 2 | 13,975 | 4,563 | ~$0.06* |
| Consolidation — Synthesizer | 2 | 18,976 | 2,621 | ~$0.06* |
| **Total Logged** | **24** | **260,279** | **55,880** | **~$1.48** |

*Consolidation invocations had $0.00 in their log files — cost estimated from Sonnet 4.6 pricing ($3/M input, $15/M output).*

### Judge Invocations by Phase

| Phase | Tasks Judged | Invocations |
|-------|-------------|-------------|
| Baseline (Phase 1) | — | Not logged (pre-logging) |
| Round 01 | 5 evolution tasks | 5 |
| Round 02 | 5 evolution tasks | 5 |
| Round 03 | 5 evolution tasks | 5 |
| Holdout post | 3 holdout tasks | 3 |
| **Total** | **18** | **18** |

Note: Baseline judge invocations and holdout pre-evaluation judge invocations were not captured in session logs (logging infrastructure was added after Phase 1). Based on similar token patterns, estimated baseline judge cost: ~$0.35.

### Executor Cost (Not Logged)

Executor invocations (Claude Opus for task execution) were not captured in session logs. The executor runs as Claude Code sub-agents, which are tracked at the session level but not in the per-invocation log format. Based on the Claude Code session costs:

| Phase | Estimated Executor Cost |
|-------|------------------------|
| Baseline (5 evolution + 3 holdout) | ~$2-4 |
| Round 01 (5 tasks) | ~$1-2 |
| Round 02 (5 tasks) | ~$1-2 |
| Round 03 (5 tasks) | ~$1-2 |
| Holdout post (3 tasks) | ~$0.50-1 |

**Estimated total executor cost:** ~$5-11

## Total Experiment Cost Estimate

| Category | Estimated Cost |
|----------|---------------|
| Judge invocations (logged) | $1.24 |
| Consolidation invocations (logged) | $0.24 |
| Judge invocations (unlogged baseline) | ~$0.35 |
| Executor invocations (unlogged) | ~$5-11 |
| Orchestration overhead (this session, analysis) | ~$2-5 |
| **Total estimate** | **~$9-18** |

**Budget utilization:** ~$9-18 of $85 ceiling = 11-21%

## Cost Per Quality Point

| Metric | Value |
|--------|-------|
| Total quality gain (evolution) | +1.58 points |
| Total quality gain (holdout) | +1.40 points |
| Estimated total cost | ~$13.50 (midpoint) |
| Cost per evolution quality point | ~$8.54 |
| Cost per holdout quality point | ~$9.64 |

## Efficiency Observations

1. **Well under budget.** The experiment used roughly 15% of the $85 ceiling. The constraint was never binding.
2. **Judge is the largest logged cost center** (84% of logged costs). Each judge invocation averages ~10,700 input tokens and ~2,450 output tokens.
3. **Consolidation is cheap.** The full critic/defender/synthesizer debate pipeline costs ~$0.12 per round — negligible compared to execution and judging.
4. **Missing executor logs** are the main gap. Future experiments should log Claude Code sub-agent costs via hooks or session metadata.
