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
rules/current/        # Symlink to active ruleset (v0/, v1/, v2/)
tasks/                # 5 evolution task specs + acceptance/
holdout/              # 3 frozen holdout tasks (EXCLUDED from executor workspace)
outputs/              # baseline/ + evolved/round-01..03/
scores/               # Judge rubric, config, score JSONs
consolidation/        # Agent prompts, debates, proposals, approvals
scripts/              # judge.py, consolidate.py, apply_rules.py
session-logs/         # Per-invocation cost/token metadata
analysis/             # Phase 4 outputs
```

## Development
- **Run tests:** `pytest tasks/acceptance/ -v`
- **Run judge:** `python scripts/judge.py --task <task-id> --output <path>`
- **Run consolidation:** `python scripts/consolidate.py --round <N>`
- **Apply rules:** `python scripts/apply_rules.py --proposal <path>`

## Safety Constraints
- All evolving rules live in `rules/` — NEVER modify `~/.claude/rules/` or `~/.claude/CLAUDE.md`
- No files written outside this project directory
- Budget ceiling: $85 total experiment cost
- Rule files: max 150 lines, no executable code blocks
- Human approval required for all rule changes

## Key Decisions
See `docs/decisions/` for ADRs.
See `GSD_PLAN.md` § "Resolved Design Decisions" for experiment design rationale.

## Sandboxed Rules
The task executor loads evolving rules from `rules/current/` (symlink to active version).
These rules govern task execution ONLY. Do not confuse with global `~/.claude/rules/`.

**Include these rules files when executing tasks:**
- `rules/current/task-executor.md`
- `rules/current/code-quality.md`
- `rules/current/output-format.md`

## Workspace Isolation
The following directories are EXCLUDED from the executor's context during evolution rounds:
- `holdout/` — frozen holdout tasks, specs, and outputs
- `consolidation/` — consolidation agent prompts and debate logs
- `scores/` — judge scores (executor must not see its own grades)
- `analysis/` — post-experiment analysis

## Notes
- The `holdout/` directory must remain isolated from the executor workspace during evolution rounds
- Judge model is Sonnet 4.6 (different from Opus executor to avoid self-grading bias)
- Every paid invocation must log session metadata to `session-logs/`
- Follow GSD plan phase ordering — respect dependency graph
