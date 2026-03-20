# Architecture — self-organizing-agents

## Overview
An experiment testing whether Claude Code sessions can progressively improve by having agents observe their own performance and evolve their behavioral rules through a critic/defender/synthesizer consolidation loop. Inspired by @agentic.james's self-organizing agent pattern.

## Tech Stack
- **Language:** Python 3.11+
- **Framework:** Claude Code (sub-agents, rules, hooks, memory)
- **Testing:** pytest (acceptance tests as ground truth)
- **Key dependencies:** anthropic SDK (judge script), pathlib, asyncio (bounded_pool task)

## Project Structure
```
├── CLAUDE.md                  # Project config (loads sandboxed rules)
├── GSD_PLAN.md                # Experiment plan (Phases 0-4)
├── rules/                     # Sandboxed evolving rules (v0/, v1/, v2/, current -> vN/)
├── tasks/                     # 5 evolution task specs + acceptance tests
├── holdout/                   # 3 frozen holdout tasks (isolated from executor)
├── outputs/                   # Task outputs (baseline/ + evolved/round-01..03/)
├── scores/                    # Judge rubric, config, score JSONs
├── consolidation/             # Critic/defender/synthesizer prompts + debate logs
├── analysis/                  # Phase 4 comparison, drift, cost, convergence, report
├── scripts/                   # judge.py, consolidate.py, apply_rules.py
├── session-logs/              # Per-invocation metadata (cost tracking)
└── docs/                      # Architecture, ADRs
```

## Entry Point
No single entry point — experiment is orchestrated via the GSD plan phases:
- `scripts/judge.py` — LLM-as-Judge scoring pipeline
- `scripts/consolidate.py` — Consolidation loop orchestrator
- `scripts/apply_rules.py` — Rule version manager

## Key Flows
- [ ] TODO: Document task execution flow (rules → executor → output → acceptance tests → judge)
- [ ] TODO: Document consolidation flow (critic → defender → synthesizer → human approval → apply)
- [ ] TODO: Document holdout evaluation flow (isolated worktree with final rules)
