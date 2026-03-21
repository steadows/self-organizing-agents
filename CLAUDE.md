# self-organizing-agents

> Extends global conventions at ~/.claude/CLAUDE.md. Project-specific rules below.

## Project Overview
Experiment testing whether Claude Code agents can improve output quality by evolving behavioral rules through a governed consolidation loop (critic/defender/synthesizer debate). Phase 1 of a 4-experiment research arc toward self-organizing multi-agent systems. Currently in Phase 0 (Setup).

## Tech Stack
- Python 3.11+
- Claude Code (sub-agents, rules/, hooks, memory)
- pytest (acceptance tests)
- anthropic SDK (LLM-as-Judge via Claude Sonnet 4.6)

## Project Structure
```
rules/exp1/           # Experiment 1 rules (frozen): v0/, v1/, v2/, current -> v2
rules/exp2/           # Experiment 2 rules (active): v0/, current, specialist dirs
tasks/exp1/           # Experiment 1: 5 task specs + acceptance/
tasks/exp2/           # Experiment 2: 8 evolution + 2 negative-control task specs
holdout/exp1/         # Experiment 1 holdout (frozen)
holdout/exp2/         # Experiment 2 holdout (EXCLUDED from executor workspace)
outputs/exp1/         # Experiment 1 outputs (frozen): baseline/ + evolved/
outputs/exp2/         # Experiment 2 outputs: baseline/, split/, control/
scores/exp1/          # Experiment 1 scores (frozen)
scores/exp2/          # Experiment 2 scores
consolidation/exp1/   # Experiment 1 consolidation (frozen)
consolidation/exp2/   # Experiment 2 consolidation: debates, proposals, approvals
scripts/              # Shared: judge.py, consolidate.py, apply_rules.py, detect_tension.py, etc.
session-logs/         # Per-invocation cost/token metadata (all experiments)
analysis/             # Post-experiment analysis (all experiments)
```

## Development
- **Run exp1 tests:** `pytest tasks/exp1/acceptance/ -v`
- **Run exp2 tests:** `pytest tasks/exp2/acceptance/ -v`
- **Run judge:** `python scripts/judge.py --task <task-id> --output <path>`
- **Run consolidation:** `python scripts/consolidate.py --round <N>`
- **Apply rules:** `python scripts/apply_rules.py --proposal <path>`

## Safety Constraints
- All evolving rules live in `rules/` — NEVER modify `~/.claude/rules/` or `~/.claude/CLAUDE.md`
- No files written outside this project directory
- Budget ceiling: $85 (Experiment 1), $450 (Experiment 2)
- Rule files: max 150 lines (exp1), shared.md max 80 / specialist max 100 lines (exp2)
- Human approval required for all rule changes

## Key Decisions
See `docs/decisions/` for ADRs.
See `GSD_PLAN.md` § "Resolved Design Decisions" for experiment design rationale.

## Sandboxed Rules
The task executor loads evolving rules from the active experiment's `current` symlink:
- **Exp1:** `rules/exp1/current/` (frozen, points to v2)
- **Exp2:** `rules/exp2/current/` (active, points to latest version)

These rules govern task execution ONLY. Do not confuse with global `~/.claude/rules/`.

**Exp1 rules files:** `task-executor.md`, `code-quality.md`, `output-format.md`
**Exp2 rules files:** Same structure pre-split. Post-split: `shared.md` + specialist dirs + `output-format.md`

## Workspace Isolation
The following directories are EXCLUDED from the executor's context during evolution rounds:
- `holdout/exp2/` — frozen holdout tasks, specs, and outputs
- `consolidation/exp2/` — consolidation agent prompts and debate logs
- `scores/exp2/` — judge scores (executor must not see its own grades)
- `analysis/` — post-experiment analysis
- `**/exp1/` — Experiment 1 artifacts (frozen, not relevant to active execution)

## Notes
- The `holdout/` directory must remain isolated from the executor workspace during evolution rounds
- Judge model is Sonnet 4.6 (different from Opus executor to avoid self-grading bias)
- Every paid invocation must log session metadata to `session-logs/`
- Follow GSD plan phase ordering — respect dependency graph
