# GSD Plan: Self-Organizing Agent Experiment in Claude Code

**Created:** 2026-03-19
**Status:** Complete — All Phases Done
**Updated:** 2026-03-20

> **RULE: Update this plan in real-time.** Mark tasks `[~]` when starting, `[x]` when done, `[!]` when blocked. Never leave stale status markers.
**Source:** @agentic.james — "AI Agents Self-Organizing Like Biological Cells" (Instagram, 2026-03-19)
**Research:** `~/research-workbench/instagram-ai-agents-self-organizing-like-biological-cells/research.html`
**Transcript:** Obsidian vault `Research/Instagram/agentic.james/2026-03-19-DWDPANXk5sC.md`

---

## Problem Statement & Impetus

**Can Claude Code sessions progressively improve by having agents observe their own performance and evolve their behavioral rules?**

@agentic.james described building an AI agent that functions like "the first cell in a multicellular organism" — seeded with instructions to self-regulate, self-optimize, and divide. His 8-agent system spontaneously developed a 24-hour review cycle: two agents read all workspaces, held contrarian debates, and modified the behavioral markdown files of every agent based on observed errors. As he put it:

> "This process almost mirrors having a forward pass through a neural network, observing the loss from the predicted values, and then doing back prop on the system to adjust the weights — or in this case, the text in the markdown files that determines the agent's behavior."

Research confirms this maps to real formalisms:
- **Textual backpropagation** — Agentic Neural Networks (Ma et al., arXiv:2506.09046, Jun 2025): textual gradients refine agent roles and prompts, surpassing MetaGPT/AutoGen baselines
- **Semantic-Topological Evolution** — HiVA (Tang et al., arXiv:2509.00189, AAAI 2026): discrete-domain surrogates for backprop with 5-10% accuracy gains
- **Scheduled meta-observation loops** — Ouroboros (Razzhigaev, 2026): background consciousness loop between tasks, 30+ self-directed evolution cycles in 24 hours
- **Multi-agent critique/refinement** — Self-Refine, PromptWizard, OpenAI Self-Evolving Agents Cookbook

**The key insight:** We don't need external frameworks. Claude Code already has every primitive this pattern requires — sub-agents for differentiation, behavioral markdown files (CLAUDE.md, rules/, skills) for "weights," hooks for lifecycle events, and memory for cross-session persistence. The question is whether wiring these together produces measurable improvement.

### Epistemic Framing

The biological metaphors in this plan — backpropagation, sleep consolidation, cell division — are borrowed from the source material as **design inspiration**, not claimed as mechanism. Experiment 1 tests a narrow, falsifiable question: does a governed prompt-evolution loop improve task output quality? It is not a test of self-organization, emergence, or agency in any strong sense. If the consolidation loop works, the explanation is "structured rule iteration with feedback improves prompts" — not "agents learned to self-organize like cells." The stronger claims belong to Experiments 2-4, which progressively relax governance to test whether emergent behavior appears. Each experiment must earn its framing independently.

### Mapping to Claude Code

| Post Concept | Claude Code Equivalent |
|---|---|
| Behavioral markdown files | `CLAUDE.md`, `~/.claude/rules/`, skills |
| Agent differentiation | Sub-agents via Agent tool (planner, reviewer, etc.) |
| Self-observation | Agents reading workspaces, git history, outputs |
| Consolidation cycle | `/loop` skill or hooks |
| Modifying behavioral files | Agents editing rules files |
| Contrarian debate | Two sub-agents with opposing directives |
| Forward pass | Agent task execution |
| Loss function | LLM-as-Judge scores |
| Backpropagation | Consolidation loop editing rules based on scores |

---

## Architecture

```
~/self-organizing-agents/
├── GSD_PLAN.md                      # This file
├── CLAUDE.md                        # Project-level config (loads sandboxed rules)
├── rules/                           # SANDBOXED evolving rules
│   ├── v0/                          # Seed rules (immutable baseline)
│   │   ├── task-executor.md         # How to implement utility functions
│   │   ├── code-quality.md          # Quality standards
│   │   └── output-format.md         # Output structure requirements
│   ├── v1/, v2/                     # Evolved versions (created during Phase 3)
│   └── current -> v0/               # Symlink to active ruleset
├── tasks/                           # Task specifications (evolution set only)
│   ├── task-001.md                  # slugify() with Unicode
│   ├── task-002.md                  # validate_email() (scoped subset)
│   ├── task-003.md                  # safe_write() atomic I/O
│   ├── task-004.md                  # retry_with_backoff() decorator
│   ├── task-005.md                  # ttl_cache() decorator
│   └── acceptance/                  # Acceptance tests for evolution tasks
│       ├── test_task_001.py
│       ├── test_task_002.py
│       ├── test_task_003.py
│       ├── test_task_004.py
│       └── test_task_005.py
├── holdout/                         # ISOLATED — excluded from executor workspace
│   ├── .gitkeep                     # Exists in repo but ignored by CLAUDE.md
│   ├── specs/                       # Holdout task specifications
│   │   ├── holdout-001.md           # parse_duration() — "2h30m" → seconds
│   │   ├── holdout-002.md           # deep_merge() — recursive dict merge
│   │   └── holdout-003.md           # bounded_pool() — async worker pool
│   ├── acceptance/                  # Holdout acceptance tests
│   │   ├── test_holdout_001.py
│   │   ├── test_holdout_002.py
│   │   └── test_holdout_003.py
│   └── outputs/                     # Holdout results (pre + post)
│       ├── pre/holdout-001..003/    # Before evolution (rules v0)
│       └── post/holdout-001..003/   # After evolution (rules v2)
├── outputs/                         # Task outputs (evolution set only)
│   ├── baseline/task-001..005/      # Phase 1: static rules
│   └── evolved/                     # Phase 3: batch consolidation
│       ├── round-01/task-001..005/  # Round 1: rules v0
│       ├── round-02/task-001..005/  # Round 2: rules v1
│       └── round-03/task-001..005/  # Round 3: rules v2
├── scores/                          # Evaluation results
│   ├── judge-rubric.md              # Frozen scoring rubric (6 dimensions, 1-10)
│   ├── judge-config.json            # Frozen: model, temperature, prompt hash
│   ├── baseline-scores.json
│   ├── evolved-scores.json
│   └── holdout-scores.json          # Pre vs post holdout comparison
├── consolidation/                   # Consolidation loop artifacts
│   ├── critic-prompt.md             # Static critic agent instructions
│   ├── defender-prompt.md           # Static defender agent instructions
│   ├── synthesizer-prompt.md        # Static synthesizer agent instructions
│   ├── approval-rubric.md           # Human approval criteria (safety + coherence)
│   ├── debates/round-01..02.md      # Full debate transcripts (2 consolidation rounds)
│   ├── proposals/round-01..02.md    # Proposed rule changes (pre-approval)
│   ├── approvals/round-01..02.md    # Approval decisions with rationale
│   └── applied/round-01..02.md      # Approved diffs
├── analysis/                        # Phase 4 outputs
│   ├── comparison.md
│   ├── drift-analysis.md
│   ├── cost-tracking.md
│   ├── convergence.md
│   └── report.md
├── session-logs/                    # Session metadata for ALL paid invocations
│   └── {type}-{phase}-{task}-{timestamp}.json  # type: executor|judge|consolidation-*
│       # Fields: invocation_type, model, session_id, timestamp, input_tokens,
│       #         output_tokens, estimated_cost_usd
└── scripts/                         # Automation
    ├── judge.py                     # LLM-as-Judge scorer
    ├── consolidate.py               # Consolidation loop orchestrator
    └── apply_rules.py               # Rule version manager
```

### Key Design Decisions

1. **Task type: Python utility function generation.** Repeatable, scorable across multiple dimensions (correctness, style, docs, edge cases, tests). Each task requests a small utility with tests. Task specs include executable acceptance tests as the primary correctness signal — the LLM judge is secondary.

2. **Dual evaluation: executable tests + LLM-as-Judge.** Acceptance tests (`tasks/acceptance/`) are the ground truth for correctness and robustness. The LLM judge scores subjective dimensions (code quality, documentation, elegance) that tests can't easily capture. This prevents rubric gaming — you can't score 10/10 on correctness if the acceptance tests fail.

3. **Frozen judge configuration.** Model, temperature, prompt, and rubric are locked in `scores/judge-config.json` before Phase 1. Judge model is **Claude Sonnet 4.6** (different from the Opus executor to avoid "grading your own homework" bias). Temperature: 0.0 for deterministic scoring.

4. **Isolated holdout task set.** 3 frozen holdout tasks are never seen during evolution rounds. Holdout specs, acceptance tests, and outputs live in a **separate directory** (`holdout/`) that is excluded from the executor's workspace via `.claude/settings.json` ignore patterns and is NOT referenced in the project `CLAUDE.md`. Holdout evaluations are run in a **fresh git worktree** containing only the final ruleset — no prior outputs, no evolution history. This prevents the executor or consolidation agents from inspecting holdout content during the experiment. If holdout scores AND holdout acceptance test pass rates both improve, the rules generalized. If only evolution-set scores improve, the rules overfit.

5. **Sandboxed rules only.** Evolving rules live in `~/self-organizing-agents/rules/`. Core `~/.claude/rules/` and `~/.claude/CLAUDE.md` are never modified.

6. **Git-versioned rule evolution.** Every rule change is a commit. Full behavioral drift history is reconstructable.

7. **Formalized human approval gate.** The human approves or rejects proposals based on a documented rubric (`consolidation/approval-rubric.md`). The human's role is restricted to **safety and coherence checks** — not quality optimization. This prevents the human from becoming the real optimizer. Every approval decision is recorded with rationale in `consolidation/approvals/`.

8. **Scoped rule changes.** The synthesizer must: (a) label each proposed change with the specific failure mode it addresses, (b) stay within a cap of 20 net new lines per rule file per round, and (c) never modify more than 2 of the 3 rule files in a single round. This enables attribution — if scores improve, you can trace it to specific rule changes.

---

## Safety Constraints

### Agent-Level Controls
- [ ] **S1: Sandbox boundary** — All rule files live in `~/self-organizing-agents/rules/`. No writes to `~/.claude/rules/`, `~/.claude/CLAUDE.md`, or any file outside the project directory
- [ ] **S2: Git versioning** — Every rule change committed with `chore: evolve rules round-N` before applying
- [ ] **S3: Hard iteration cap** — Maximum 26 task runs (5 baseline + 15 evolved + 6 holdout). 2 consolidation rounds. No unbounded loops
- [ ] **S4: Human approval gate** — Consolidation outputs proposals. Human reviews against `consolidation/approval-rubric.md` (safety + coherence only, not quality optimization). Decision + rationale recorded in `consolidation/approvals/`
- [ ] **S5: Frozen judge** — LLM-as-Judge model, temperature, rubric, and prompt are locked in `scores/judge-config.json` before Phase 1. Immutable throughout the experiment
- [ ] **S6: No self-referential evolution** — Evolving rules govern task execution only. Consolidation loop instructions are static
- [ ] **S7: Kill switch** — If any iteration produces rules instructing the agent to modify files outside the sandbox, halt immediately
- [ ] **S8: Scoped changes** — Synthesizer limited to 20 net new lines per rule file per round, max 2 of 3 rule files per round. Each change must cite the failure mode it addresses

### Infrastructure-Level Controls (Do Not Depend on Agent Compliance)
- [ ] **S9: Budget ceiling** — Hard stop if cumulative cost exceeds $85. Enforced via API budget tracking, not agent self-reporting. Check `session-logs/` (all invocation types) after each round. Estimate breakdown: 26 executor runs (~$2-5 each = $52-130) + 78 judge calls (26 outputs x 3 runs each, Sonnet ~$0.10-0.20 = $8-16) + 2 consolidation rounds (3 agents each ~$5-10 = $10-20) ≈ $70-85 at median. If early rounds track high, reduce to 2 evolved rounds instead of 3
- [ ] **S10: Rule file size cap** — No individual rule file may exceed 150 lines. `apply_rules.py` rejects proposals that would exceed this. Prevents runaway rule bloat
- [ ] **S11: Rule file schema validation** — `apply_rules.py` validates that rule files are valid markdown with no executable code blocks (no `bash`, `python`, `sh` fenced blocks that could be interpreted as instructions to run commands). Only prose and pseudocode allowed
- [ ] **S12: Session metadata logging** — Every paid invocation (task execution, judge evaluation, consolidation agent call) logs a distinct entry to `session-logs/` with: invocation type (`executor` | `judge` | `consolidation-critic` | `consolidation-defender` | `consolidation-synthesizer`), model version, session ID, timestamp, input/output token counts, and estimated cost. This is mandatory for reproducibility, cost tracking, and budget enforcement

---

## Phase 0: Project Setup

**Goal:** Initialize experiment directory, git repo, seed rules, tasks, acceptance tests, holdout set, and judge.
**Estimated effort:** 1-2 hours
**Status:** ✅ COMPLETE (2026-03-20)

- [x] **0.1** Create project directory structure (see Architecture above)
- [x] **0.2** Initialize git repo + `.gitignore`
- [x] **0.3** Write project `CLAUDE.md` that loads sandboxed rules from `rules/current/`
- [x] **0.4** Write seed rules `v0/` — deliberately imperfect (e.g., vague test requirements, missing edge case guidance) to leave room for improvement
  - `task-executor.md` — Core instructions for implementing Python utilities
  - `code-quality.md` — Quality standards: type hints, docstrings, structure
  - `output-format.md` — Output structure: file naming, required sections
- [x] **0.5** Create symlink `rules/current -> rules/v0`
- [x] **0.6** Design 5 evolution task specs (`tasks/`) — each must include: function signature, explicit edge-case policy decisions (not left ambiguous), input/output examples, and a "scope boundary" statement clarifying what is NOT required:
  1. `tasks/task-001.md` — `slugify()` with Unicode support. Scope: ASCII transliteration only (no full ICU), separator is always `-`, max length 200
  2. `tasks/task-002.md` — `validate_email()` — scoped to: local-part + `@` + domain, no quoted strings, no IP literals, no comments. Explicit list of valid/invalid examples
  3. `tasks/task-003.md` — `safe_write()` with atomic writes via temp file + rename. Scope: POSIX only, no Windows support, no rollback beyond single-file
  4. `tasks/task-004.md` — `retry_with_backoff()` decorator with exponential backoff + jitter. Scope: configurable max retries, base delay, max delay. No circuit breaker
  5. `tasks/task-005.md` — `ttl_cache()` decorator with size limit (LRU eviction) and time-based expiration. Scope: thread-safe, no distributed caching
- [x] **0.7** Design 3 frozen holdout task specs (`holdout/specs/`) — these are NEVER seen during evolution rounds. The entire `holdout/` directory is excluded from the executor workspace via CLAUDE.md ignore patterns:
  1. `holdout/specs/holdout-001.md` — `parse_duration("2h30m10s")` → integer seconds. Support h/m/s units
  2. `holdout/specs/holdout-002.md` — `deep_merge(base, override)` → recursive dict merge, lists replaced not appended
  3. `holdout/specs/holdout-003.md` — `bounded_pool(max_workers, max_queue)` → async worker pool with backpressure
- [x] **0.8** **`/steadows-tdd`** — Write executable acceptance tests for all 8 tasks. Evolution tests go in `tasks/acceptance/test_task_*.py`. Holdout tests go in `holdout/acceptance/test_holdout_*.py`. These are the ground truth for correctness. Each test file must cover: happy path, edge cases listed in the task spec, and at least one error/invalid input case. These tests are frozen — they do not evolve
- [x] **0.9** Write judge rubric (`scores/judge-rubric.md`) — 6 dimensions, each 1-10. Dimensions 1-2 are validated by acceptance tests (judge score must be consistent with test pass/fail). Dimensions 3-6 are subjective:
  1. Correctness — handles all specified requirements? **(cross-checked against acceptance tests)**
  2. Edge cases — boundary conditions, empty inputs, error states? **(cross-checked against acceptance tests)**
  3. Code quality — type hints, naming, structure, immutability?
  4. Documentation — docstrings, usage examples?
  5. Test coverage — happy path + edge cases in the agent's own tests?
  6. Robustness — error handling, input validation, graceful degradation?
- [x] **0.10** Freeze judge configuration (`scores/judge-config.json`):
  - Model: `claude-sonnet-4-6` (different from Opus executor — avoids self-grading bias)
  - Temperature: `0.0` (deterministic scoring)
  - Prompt: hash-locked (SHA-256 of the full judge prompt stored in config)
  - Rubric version: hash-locked
- [x] **0.11** Write human approval rubric (`consolidation/approval-rubric.md`). The human approves or rejects proposals based on:
  1. **Safety:** Does the proposal stay within sandbox? No instructions to access external systems?
  2. **Coherence:** Are the rules internally consistent? No contradictions with existing rules?
  3. **Scope:** Does the proposal stay within the 20-line-per-file, 2-file-per-round cap?
  4. **Attribution:** Is each change labeled with the failure mode it addresses?
  - The human does NOT evaluate whether the change will improve quality — that's the experiment's job to measure
  - Every decision recorded with rationale in `consolidation/approvals/round-NN.md`
- [x] **0.12** **`/steadows-tdd`** — Run TDD workflow BEFORE writing `scripts/judge.py`. Write tests for: score parsing, rubric loading, JSON output format, acceptance test cross-check (judge correctness score must be <= 5 if acceptance tests fail), config loading from `judge-config.json`
- [x] **0.13** Write judge script (`scripts/judge.py`) — must pass tests from 0.12. Reads output + rubric + config, calls Claude Sonnet at temperature 0.0, runs acceptance tests, parses 6-dimension scores to JSON, flags any correctness/edge-case score inconsistent with test results
- [x] **0.14** Human spot-check: manually review 2-3 judge outputs for calibration. Verify scores feel reasonable before trusting the judge for the full experiment
- [x] **0.15** Initial git commit: `chore: initialize self-organizing agent experiment`
- [x] **0.16** **`/steadows-verify`** — Phase 0 quality gate. Verify: project structure exists, git repo initialized, seed rules valid, all 8 task specs complete with scoped boundaries, all 8 acceptance test files pass (against reference implementations), judge script passes tests, judge-config.json frozen, approval rubric exists, no files written outside sandbox

---

## Phase 1: Baseline with Static Rules

**Goal:** Run all 5 evolution tasks + 3 holdout tasks with v0 seed rules. No consolidation. Record acceptance test results + LLM-as-Judge scores. This is the control measurement.
**Estimated effort:** 1-2 hours
**Dependency:** Phase 0 complete
**Session logging:** Every task run must log session metadata to `session-logs/` (model version, session ID, timestamp, token counts)
**Status:** ✅ COMPLETE (2026-03-20) — Note: session logs not captured for baseline runs (gap identified)

### Evolution Task Baseline (5 tasks, concurrent)

- [x] **1.1** Run task-001 with static rules → `outputs/baseline/task-001/`
- [x] **1.2** Run task-002 with static rules → `outputs/baseline/task-002/`
- [x] **1.3** Run task-003 with static rules → `outputs/baseline/task-003/`
- [x] **1.4** Run task-004 with static rules → `outputs/baseline/task-004/`
- [x] **1.5** Run task-005 with static rules → `outputs/baseline/task-005/`
- [x] **1.6** Run acceptance tests against all 5 outputs. Record pass/fail per test case
- [x] **1.7** Judge all 5 outputs (run 3x each, take median). Cross-check: if acceptance tests fail, judge correctness score must be <= 5

### Holdout Task Baseline (3 tasks — run in isolated worktree)

Holdout evaluations run in a **fresh git worktree** containing only `rules/v0/` + `holdout/` directory. The main workspace never sees holdout content during evolution.

**Artifact flow:** Holdout outputs, acceptance test results, and judge scores are all produced inside the worktree's `holdout/` directory. After evaluation completes, **scores only** (JSON) are copied to the main repo's `scores/` directory. Holdout outputs remain in `holdout/outputs/` (committed to the repo but excluded from the executor workspace via CLAUDE.md ignore patterns). The `/steadows-verify` gate verifies holdout outputs exist by reading `holdout/outputs/` directly — not by expecting them in `outputs/`.

- [x] **1.8** Create isolated worktree for holdout pre-evaluation (rules v0 + `holdout/` directory)
- [x] **1.9** Run holdout-001 in worktree → `holdout/outputs/pre/holdout-001/`
- [x] **1.10** Run holdout-002 in worktree → `holdout/outputs/pre/holdout-002/`
- [x] **1.11** Run holdout-003 in worktree → `holdout/outputs/pre/holdout-003/`
- [x] **1.12** Run holdout acceptance tests in worktree against all 3 outputs. Record pass/fail per test case
- [x] **1.13** Judge all 3 holdout outputs in worktree (same 3x median protocol)
- [x] **1.14** Commit holdout outputs + scores inside worktree. Merge worktree branch to main. Delete worktree. Holdout outputs now exist in `holdout/outputs/pre/` in the repo but remain excluded from executor workspace via CLAUDE.md

### Compile and Checkpoint

- [x] **1.15** Compile baseline scores → `scores/baseline-scores.json` (per-dimension averages + overall, evolution set and holdout set separately)
- [x] **1.16** Git checkpoint: `data: baseline scores (5 evolution + 3 holdout, static rules v0)`
- [x] **1.17** **`/steadows-verify`** — Phase 1 quality gate. Verify: all 5 evolution outputs exist in `outputs/baseline/`, all 3 holdout outputs exist in `holdout/outputs/pre/`, all acceptance tests ran with recorded results, all judge scores recorded in JSON with 3x medians, scores are within valid range (1-10), correctness scores consistent with acceptance test results, baseline-scores.json aggregation is correct, session logs captured for all 8 runs (all invocation types: executor + judge), no rule files were modified during baseline

---

## Phase 2: Consolidation Loop Implementation

**Goal:** Build the critic/defender/synthesizer debate pattern.
**Estimated effort:** 2-3 hours
**Dependency:** Phase 0 complete (can run in parallel with Phase 1)
**Status:** ✅ COMPLETE (2026-03-20)

### 2A: Agent Design

- [x] **2.1** Design critic agent prompt (`consolidation/critic-prompt.md`)
  - Reads current rules + task output + judge scores
  - Identifies weaknesses traceable to rule gaps
  - Output: "Rule X is missing guidance on Y, causing deficiency Z"
  - This agent finds the **textual gradient** — the direction rules should change

- [x] **2.2** Design defender agent prompt (`consolidation/defender-prompt.md`)
  - Reads critic's proposals
  - Argues AGAINST each change: potential regressions, over-specification, bloat
  - Rates each proposal: ACCEPT / REJECT / MODIFY
  - Calibration: aggressive enough to prevent runaway growth, not so aggressive nothing evolves

- [x] **2.3** Design synthesizer agent prompt (`consolidation/synthesizer-prompt.md`)
  - Reads critic proposals + defender responses
  - Resolves disagreements into minimal rule diffs
  - **Constrained output:** each change must cite the specific failure mode it addresses. Max 20 net new lines per rule file. Max 2 of 3 rule files modified per round
  - Output: exact additions/modifications/deletions to rule files with attribution labels
  - This agent is the **gradient update step**

### 2B: Orchestration

- [x] **2.4** **`/steadows-tdd`** — Run TDD workflow BEFORE writing `scripts/consolidate.py`. Write tests for: prompt assembly from rule files + outputs + scores, critic/defender/synthesizer invocation sequence, proposal file output format, debate transcript capture. Then implement
- [x] **2.5** Implement consolidation orchestrator (`scripts/consolidate.py`) — must pass tests from 2.4
  - Collects: current rules + latest output + judge scores
  - Invokes critic → defender → synthesizer (sequential, each feeds the next)
  - Writes proposal to `consolidation/proposals/round-NN-proposal.md`
  - Writes debate transcript to `consolidation/debates/round-NN.md`
  - **STOPS and waits for human approval** — does NOT apply changes

- [x] **2.6** **`/steadows-tdd`** — Run TDD workflow BEFORE writing `scripts/apply_rules.py`. Write tests for: version directory creation, rule file copying, symlink update, rollback on failure, 150-line-per-file rejection, schema validation (no executable code blocks), change scope enforcement (20-line cap, 2-file cap). Then implement
- [x] **2.7** Implement rule applicator (`scripts/apply_rules.py`) — must pass tests from 2.6
  - Reads approved proposal
  - **Validates:** rule file stays under 150 lines, no executable code blocks (`bash`, `python`, `sh`), change scope within caps
  - Copies current rules to `rules/vN/`
  - Applies changes
  - Updates `rules/current` symlink
  - Commits: `chore: evolve rules round-N`

- [x] **2.8** End-to-end test of consolidation loop using one baseline output
- [x] **2.9** Git checkpoint: `feat: consolidation loop (critic/defender/synthesizer)`
- [x] **2.10** **`/steadows-verify`** — Phase 2 quality gate. Verify: all 3 agent prompts exist and are well-formed, consolidate.py passes all tests, apply_rules.py passes all tests, end-to-end test produces valid proposal + debate transcript, symlink management works correctly, no files written outside sandbox

---

## Phase 3: Evolved Iterations (Batch Consolidation)

**Goal:** Run the same 5 tasks with consolidation active. Rules evolve after each **batch** of 5 tasks, not after each individual task. Run 3 rounds to give the consolidation loop enough signal to converge.
**Estimated effort:** 3-4 hours total across 4 sessions
**Dependency:** Phase 1 + Phase 2 complete
**Status:** 🔵 IN PROGRESS

**Why batch consolidation:** Consolidating after a single task gives the critic one data point — not enough to distinguish a rule gap from a task-specific quirk. Batch consolidation gives 5 diverse outputs per round, producing higher-quality rule updates with less noise.

**Session logging:** Every task run must log session metadata to `session-logs/` (model version, session ID, timestamp, token counts).

**Context management:** Phase 3 is split into 4 sub-phases, each designed to fit in a single context window. Start each sub-phase in a **fresh session**. Load context from the latest snapshot in `.context/snapshots/`. **All task execution MUST use subagents (Agent tool)** — never run tasks directly in the main session. This keeps task outputs out of the orchestrating context window and prevents compaction.

---

## Phase 3A: Round 1 — Execute + Consolidate (rules v0 → v1)

**Start:** Fresh session. Load `.context/snapshots/` (latest) + `GSD_PLAN.md` Phase 3A section + `rules/v0/*.md` + `scores/baseline-scores.json`.
**End:** `rules/v1/` created, checkpoint taken, context reset.

Tasks within a round are independent — launch all 5 as concurrent subagents.

- [x] **3A.1** Launch 5 concurrent subagents (one per task) to execute tasks with rules v0:
  - Subagent 1: task-001 → `outputs/evolved/round-01/task-001/`
  - Subagent 2: task-002 → `outputs/evolved/round-01/task-002/`
  - Subagent 3: task-003 → `outputs/evolved/round-01/task-003/`
  - Subagent 4: task-004 → `outputs/evolved/round-01/task-004/`
  - Subagent 5: task-005 → `outputs/evolved/round-01/task-005/`
  - Each subagent reads `tasks/task-00N.md` + `rules/current/*.md` and writes output to its designated directory
- [x] **3A.2** Run acceptance tests against all 5 outputs: `pytest tasks/acceptance/ -v`
- [x] **3A.3** Judge all 5 outputs via `python scripts/judge.py` (run 3x each, take median). Cross-check against acceptance test results
- [x] **3A.4** Run consolidation: `python scripts/consolidate.py --round 01` → critic/defender/synthesizer review ALL 5 outputs + scores + acceptance results → proposal written to `consolidation/proposals/round-01.md`, debate to `consolidation/debates/round-01.md`
- [x] **3A.5** 🔒 **Human approval gate:** Review `consolidation/proposals/round-01.md` against `consolidation/approval-rubric.md` → record decision + rationale in `consolidation/approvals/round-01.md`
- [x] **3A.6** If approved: `python scripts/apply_rules.py --proposal consolidation/proposals/round-01.md` → creates `rules/v1/`, updates `rules/current` symlink
- [x] **3A.7** Git checkpoint: `data: evolved round 1 scores + rules v1`
- [x] **3A.8** **`/steadows-checkpoint`** — snapshot before context reset

**→ Reset context before Phase 3B.**

---

## Phase 3B: Round 2 — Execute + Consolidate (rules v1 → v2)

**Start:** Fresh session. Load `.context/snapshots/` (latest) + `GSD_PLAN.md` Phase 3B section + `rules/v1/*.md` + `scores/baseline-scores.json`.
**End:** `rules/v2/` created, checkpoint taken, context reset.

- [x] **3B.1** Launch 5 concurrent subagents (one per task) to execute tasks with rules v1:
  - Subagent 1: task-001 → `outputs/evolved/round-02/task-001/`
  - Subagent 2: task-002 → `outputs/evolved/round-02/task-002/`
  - Subagent 3: task-003 → `outputs/evolved/round-02/task-003/`
  - Subagent 4: task-004 → `outputs/evolved/round-02/task-004/`
  - Subagent 5: task-005 → `outputs/evolved/round-02/task-005/`
  - Each subagent reads `tasks/task-00N.md` + `rules/current/*.md` and writes output to its designated directory
- [x] **3B.2** Run acceptance tests against all 5 outputs: `pytest tasks/acceptance/ -v`
- [x] **3B.3** Judge all 5 outputs via `python scripts/judge.py` (run 3x each, take median). Cross-check against acceptance test results
- [x] **3B.4** Run consolidation: `python scripts/consolidate.py --round 02` → proposal to `consolidation/proposals/round-02.md`, debate to `consolidation/debates/round-02.md`
- [x] **3B.5** 🔒 **Human approval gate:** Review `consolidation/proposals/round-02.md` → record decision + rationale in `consolidation/approvals/round-02.md`
- [x] **3B.6** If approved: `python scripts/apply_rules.py --proposal consolidation/proposals/round-02.md` → creates `rules/v2/`, updates `rules/current` symlink
- [x] **3B.7** Git checkpoint: `data: evolved round 2 scores + rules v2`
- [ ] **3B.8** **`/steadows-checkpoint`** — snapshot before context reset

**→ Reset context before Phase 3C.**

---

## Phase 3C: Round 3 + Holdout (final measurement, rules v2)

**Start:** Fresh session. Load `.context/snapshots/` (latest) + `GSD_PLAN.md` Phase 3C section + `rules/v2/*.md`.
**End:** All final scores recorded, holdout post-eval complete, context reset.

### Round 3 — Final measurement (no consolidation)

- [x] **3C.1** Launch 5 concurrent subagents (one per task) to execute tasks with rules v2:
  - Subagent 1: task-001 → `outputs/evolved/round-03/task-001/`
  - Subagent 2: task-002 → `outputs/evolved/round-03/task-002/`
  - Subagent 3: task-003 → `outputs/evolved/round-03/task-003/`
  - Subagent 4: task-004 → `outputs/evolved/round-03/task-004/`
  - Subagent 5: task-005 → `outputs/evolved/round-03/task-005/`
- [x] **3C.2** Run acceptance tests against all 5 outputs: `pytest tasks/acceptance/ -v`
- [x] **3C.3** Judge all 5 outputs via `python scripts/judge.py` (run 3x each, take median). No consolidation — this is the final measurement

### Holdout Post-Evaluation (generalization test — isolated worktree)

Run in a **fresh git worktree** containing only `rules/v2/` + `holdout/` directory. No evolution outputs visible. Same artifact flow as Phase 1 holdout.

- [x] **3C.4** Create isolated worktree for holdout post-evaluation (rules v2 + `holdout/` directory)
- [x] **3C.5** Launch 3 concurrent subagents in the worktree to execute holdout tasks with rules v2:
  - Subagent 1: holdout-001 → `holdout/outputs/post/holdout-001/`
  - Subagent 2: holdout-002 → `holdout/outputs/post/holdout-002/`
  - Subagent 3: holdout-003 → `holdout/outputs/post/holdout-003/`
- [x] **3C.6** Run holdout acceptance tests in worktree: `pytest holdout/acceptance/ -v`. Record pass/fail per test case
- [x] **3C.7** Judge all 3 holdout outputs in worktree (same 3x median protocol)
- [x] **3C.8** Commit holdout post outputs + scores inside worktree. Merge worktree branch to main. Delete worktree

### Compile and Checkpoint

- [x] **3C.9** Compile all evolved scores → `scores/evolved-scores.json` (per-round, per-task, per-dimension)
- [x] **3C.10** Compile holdout scores → `scores/holdout-scores.json` (pre vs post, per-task, per-dimension, including acceptance test pass rates)
- [x] **3C.11** Git checkpoint: `data: evolved round 3 + holdout post scores (final)`
- [x] **3C.12** **`/steadows-checkpoint`** — snapshot before context reset

**→ Reset context before Phase 3D.**

---

## Phase 3D: Verify

**Start:** Fresh session. Load `.context/snapshots/` (latest) + `GSD_PLAN.md` Phase 3D section.
**End:** Phase 3 quality gate passed.

- [x] **3D.1** **`/steadows-verify`** — Phase 3 quality gate. Verify: all 15 evolved outputs exist in `outputs/evolved/` (5 tasks x 3 rounds), all 3 holdout pre outputs exist in `holdout/outputs/pre/`, all 3 holdout post outputs exist in `holdout/outputs/post/`, all acceptance tests ran per round with recorded results, all judge scores recorded with 3x medians, correctness scores consistent with acceptance results, 2 consolidation proposals generated with approval rationales recorded in `consolidation/approvals/`, rules versions v1-v2 exist with valid diffs and attribution labels, each rule file under 150 lines, `rules/current` symlink points to v2, all session logs captured (all invocation types: executor + judge + consolidation agents), no files modified outside sandbox

---

## Phase 4: Measurement & Analysis

**Goal:** Compare baseline vs evolved. Analyze rule drift. Report findings.
**Estimated effort:** 1-2 hours
**Dependency:** Phase 1 + Phase 3 complete

- [x] **4.1** Score comparison (`analysis/comparison.md`) — baseline vs round 1 vs round 2 vs round 3, per-dimension and overall deltas, per-task trends across rounds. Include both LLM judge scores and acceptance test pass rates
- [x] **4.2** Holdout generalization analysis (`analysis/holdout-analysis.md`) — compare holdout pre (rules v0) vs holdout post (rules v2). **This is the key generalization test.** If holdout scores improve, the rules generalized beyond the 5 evolution tasks. If only evolution-set scores improve, the rules overfit. Report the delta with the same rigor as the main comparison
- [x] **4.3** Behavioral drift analysis (`analysis/drift-analysis.md`) — diff rules v0→v1→v2, categorize changes (new guidance, clarification, removal, restructuring), flag bloat, measure rule file growth in lines, verify all changes have attribution labels
- [x] **4.4** Cost tracking (`analysis/cost-tracking.md`) — tokens per round from `session-logs/`, broken down by invocation type (executor, judge, consolidation). Cost per quality-point improvement. Baseline phase vs evolved phase total. Total experiment cost vs $85 budget ceiling
- [x] **4.5** Convergence analysis (`analysis/convergence.md`) — do per-round averages improve monotonically? does round 3 plateau vs round 2? which dimensions converge fastest? do any tasks resist improvement across all rounds? do acceptance test pass rates correlate with judge scores?
- [x] **4.6** Experiment report (`analysis/report.md`) — hypothesis, methodology, results (including holdout), findings, limitations (including: human approval as confound, task complexity ceiling, model-specific results), recommendations for whether to proceed to Experiment 2
- [x] **4.7** Dev journal entry (`~/dev-journal/2026-03-XX.md`)
- [x] **4.8** Final git commit: `docs: experiment analysis and report`
- [x] **4.9** **`/steadows-verify`** — Phase 4 quality gate (final). Verify: all analysis files exist, comparison includes per-dimension deltas, holdout analysis explicitly states generalization verdict, drift analysis covers all rule versions with attribution labels, cost tracking sourced from session-logs with per-round breakdown, convergence analysis addresses plateau question, report includes methodology + results + holdout + limitations, all success criteria evaluated, experiment is fully reproducible from git history

---

## Dependency Graph & Concurrency Lanes

### Phase-Level Dependencies

```
Phase 0 (Setup)
  ├──> Phase 1 (Baseline)  ──────────────────────┐
  │                                               │
  └──> Phase 2 (Consolidation Loop) ─┐           │
                                      │           │
                                      ▼           ▼
                                Phase 3 (Evolved Iterations)
                                      │
                                      ▼
                                Phase 4 (Analysis)
```

### Concurrency Lane A: Baseline Execution (Phase 1)

After Phase 0 completes, this lane runs all 8 baseline tasks (5 evolution + 3 holdout) with static rules.
No dependencies between tasks — all 8 can run concurrently in separate sessions.

```
Lane A Timeline (after Phase 0):
┌──────────────────────────────────────────────────────────────────┐
│  MAIN WORKSPACE:                                                 │
│    A1: task-001 ────┐                                            │
│    A2: task-002 ────┤                                            │
│    A3: task-003 ────┼──> 1.6 acceptance ──> 1.7 judge all        │
│    A4: task-004 ────┤                                            │
│    A5: task-005 ────┘                                            │
│                                                                  │
│  ISOLATED WORKTREE (concurrent):                                 │
│    A6: holdout-001 ─┐                                            │
│    A7: holdout-002 ─┼──> 1.12 acceptance ──> 1.13 judge all     │
│    A8: holdout-003 ─┘                                            │
│                                                                  │
│  1.15 Compile ──> 1.17 /steadows-verify                          │
└──────────────────────────────────────────────────────────────────┘
```

**Parallelism:** Evolution tasks (1.1-1.5) run concurrently in main workspace.
Holdout tasks (1.9-1.11) run concurrently in an isolated worktree.
Both lanes can run in parallel — they share no workspace state.
Steps 1.15 (compile) and 1.17 (`/steadows-verify`) are sequential barriers.

### Concurrency Lane B: Consolidation Loop Build (Phase 2)

Runs in parallel with Lane A. No dependency on baseline outputs until step 2.8 (E2E test).

```
Lane B Timeline (after Phase 0):
┌──────────────────────────────────────────────────────────────────────┐
│  B1: Agent prompt design (2.1, 2.2, 2.3) ─────────────┐             │
│       2.1 critic ──┐                                    │             │
│       2.2 defender ─┼──(2.3 synthesizer depends on both)│             │
│                     │                                    │             │
│  B2: /steadows-tdd + consolidate.py (2.4, 2.5) ────────┤             │
│  B3: /steadows-tdd + apply_rules.py (2.6, 2.7) ────────┤             │
│       (B2 and B3 can run in parallel)                   │             │
│                                                          │             │
│  B4: E2E test (2.8) ◄── requires one output from Lane A │             │
│  B5: Git checkpoint (2.9) ──> 2.10 /steadows-verify     │             │
└──────────────────────────────────────────────────────────────────────┘
```

**Parallelism within Lane B:**
- 2.1 (critic) and 2.2 (defender) prompts can be written concurrently. 2.3 (synthesizer) depends on both
- 2.4-2.5 (consolidate.py) and 2.6-2.7 (apply_rules.py) can be developed concurrently — they are separate scripts with independent TDD cycles
- 2.8 (E2E test) is the **join point** between Lane A and Lane B — needs at least one baseline output from Lane A

### Cross-Lane Synchronization

```
Lane A ──────────────────────────────┐
  (any one task+judge pair finishes)  │
                                      ├──> 2.8 E2E test (Lane B)
Lane B ──────────────────────────────┘
  (consolidate.py + apply_rules.py ready)

Lane A (all 8 tasks done + /verify) ─┐
                                      ├──> Phase 3 (batch rounds)
Lane B (E2E test done + /verify) ────┘
```

### Phase 3: Batch Consolidation (Intra-Round Concurrency)

Each round runs 5 tasks concurrently, then tests + judges + consolidates. Rounds are sequential.

```
Phase 3 Timeline:
┌──────────────────────────────────────────────────────────────────────────┐
│  ROUND 1 (rules v0):                                                    │
│    3.1 task-001 ─┐                                                       │
│    3.2 task-002 ─┤                                                       │
│    3.3 task-003 ─┼─> 3.6 acceptance ─> 3.7 judge ─> 3.8 consolidate    │
│    3.4 task-004 ─┤        tests                          │               │
│    3.5 task-005 ─┘                                  🔒 approve           │
│                                                          ▼               │
│                                                      rules v1            │
│  ROUND 2 (rules v1):                                                    │
│    3.10 task-001 ─┐                                                      │
│    3.11 task-002 ─┤                                                      │
│    3.12 task-003 ─┼─> 3.15 acceptance ─> 3.16 judge ─> 3.17 consolidate│
│    3.13 task-004 ─┤         tests                          │             │
│    3.14 task-005 ─┘                                   🔒 approve         │
│                                                            ▼             │
│                                                        rules v2          │
│  ROUND 3 (rules v2) — final measurement:                                │
│    3.19 task-001 ─┐                                                      │
│    3.20 task-002 ─┤                                                      │
│    3.21 task-003 ─┼─> 3.24 acceptance ─> 3.25 judge                     │
│    3.22 task-004 ─┤         tests              │                         │
│    3.23 task-005 ─┘                             ▼                        │
│                                          (no consolidation)              │
│  HOLDOUT POST-EVAL (rules v2, isolated worktree):                        │
│    3.27 holdout-001 ─┐                                                   │
│    3.28 holdout-002 ─┼─> 3.30 acceptance ─> 3.31 judge                  │
│    3.29 holdout-003 ─┘       tests                                       │
│                                                                          │
│  3.33 compile ──> 3.34 holdout compile ──> 3.36 /steadows-verify        │
└──────────────────────────────────────────────────────────────────────────┘
```

**Intra-round parallelism:** 5 tasks per round run concurrently in separate sessions.
**Inter-round sequential:** Each round waits for the previous consolidation to complete.
**Human approval gate** (🔒) blocks between rounds (steps 3.8 and 3.17). Decision + rationale recorded.
**Round 3 has no consolidation** — it's the final measurement of the v2 rules.
**Holdout post-eval** runs after round 3 with the same v2 rules. Concurrent with round 3 compile.

### Phase 4: Partial Concurrency

```
Phase 4 Timeline (after Phase 3):
┌──────────────────────────────────────────────────────────┐
│  4.1 score comparison ──────┐                            │
│  4.2 holdout analysis ──────┤                            │
│  4.3 drift analysis ────────┼──> 4.6 report              │
│  4.4 cost tracking ─────────┤       │                    │
│  4.5 convergence analysis ──┘       ▼                    │
│                               4.7 dev journal            │
│                               4.8 git commit             │
│                               4.9 /steadows-verify       │
└──────────────────────────────────────────────────────────┘
```

**Parallelism:** 4.1-4.5 are independent analyses — run concurrently.
4.6 (report) joins all five, then 4.7-4.9 are sequential.

### TDD & Verify Gate Summary

| Gate | Phase | Skill | What It Guards |
|---|---|---|---|
| 0.8 | Setup | `/steadows-tdd` | Acceptance tests for all 8 tasks — tests before implementations |
| 0.12 | Setup | `/steadows-tdd` | `scripts/judge.py` — tests before code |
| 0.16 | Setup | `/steadows-verify` | Project structure, seed rules, all task specs, acceptance tests, judge script, frozen config |
| 1.17 | Baseline | `/steadows-verify` | All 8 outputs (5 main + 3 isolated holdout), acceptance tests, judge scores, session logs, data integrity |
| 2.4 | Consolidation | `/steadows-tdd` | `scripts/consolidate.py` — tests before code |
| 2.6 | Consolidation | `/steadows-tdd` | `scripts/apply_rules.py` — tests before code (including validation: 150-line cap, schema, change scope) |
| 2.10 | Consolidation | `/steadows-verify` | Agent prompts, approval rubric, scripts, E2E test, sandbox |
| 3D.1 | Evolved | `/steadows-verify` | All 15 evolved + 6 isolated holdout outputs, acceptance tests, scores, rule versions, approval records with rationale, session logs (all invocation types), sandbox |
| 4.9 | Analysis | `/steadows-verify` | All analysis files including holdout generalization verdict, report, reproducibility |

**CRITICAL: `/steadows-tdd` and `/steadows-verify` are the canonical skill names. Do NOT substitute with alternative tools, manual checks, or ad-hoc test runs. Invoke these skills exactly as named.**

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Rules evolve but scores don't improve | Medium | Valid experimental outcome — document it. Check judge sensitivity and acceptance test granularity |
| Rules overfit to evolution tasks (scores up, holdout flat) | High | Holdout task set catches this. If SC11 fails, the result is "rules memorized 5 tasks" not "rules improved" |
| Rules become bloated/contradictory | Medium | Defender agent pushes back. 150-line hard cap in apply_rules.py. 20-line-per-file change cap per round |
| LLM-as-Judge inconsistency | Medium | Run 3x per output, take median. Sonnet judge (not Opus executor). Temperature 0.0. Cross-check against acceptance tests |
| Judge-acceptance test disagreement | Medium | If judge says 9/10 correctness but acceptance tests fail, flag for investigation. Judge score capped at 5 when tests fail |
| Consolidation produces nonsensical changes | Medium | Human approval gate with documented rubric. Synthesizer must attribute each change to a failure mode |
| Human becomes the real optimizer | Medium | Approval rubric restricts human to safety + coherence only, not quality judgment. Rationale recorded for auditability |
| Cost exceeds budget | Low | Track from session-logs (all invocation types) after each round. Hard stop at $85. Estimate: 26 executor runs + 78 judge calls + 6 consolidation agent calls ≈ $70-85 at median |
| Sandbox escape | Critical | apply_rules.py validates: no files outside project, no executable code blocks in rules, file size under 150 lines |
| Concurrency noise | Low | Session metadata logged. If results are noisy, re-run sequential as diagnostic |
| Confounding variables | Medium | Same tasks, same order, same executor model (Opus), different judge model (Sonnet), separate sessions. Claude Code version logged |

---

## Success Criteria

### Execution Criteria (must pass for the experiment to be valid)
- [ ] **SC1:** All 8 baseline runs complete with valid judge scores and acceptance test results
- [ ] **SC2:** All 15 evolved runs + 6 holdout runs complete with valid scores
- [ ] **SC3:** Consolidation loop produces at least 2 non-trivial rule changes across 2 rounds, each with attribution labels
- [ ] **SC4:** Total experiment cost stays under $85 (sourced from session-logs covering all invocation types, not estimates)
- [ ] **SC5:** All rule changes are git-versioned; no files outside sandbox modified; all rule files under 150 lines
- [ ] **SC6:** All human approval decisions recorded with rationale

### Outcome Criteria (determines whether the experiment "worked")
- [ ] **SC7:** Mean round 3 evolved score exceeds mean baseline score by >= 0.5 points (on 1-10 scale)
- [ ] **SC8:** No evolved dimension regresses below baseline by more than 1 point
- [ ] **SC9:** Scores show monotonic improvement across rounds (round 2 > round 1, round 3 > round 2) on at least 4 of 6 dimensions
- [ ] **SC10:** Acceptance test pass rate in round 3 >= acceptance test pass rate in baseline
- [ ] **SC11: Generalization (the critical test):** Holdout post scores (rules v2) exceed holdout pre scores (rules v0) by >= 0.3 points AND holdout post acceptance test pass rate >= holdout pre pass rate. Both conditions required — score improvement without acceptance test improvement is not generalization. If this fails but SC7 passes, the rules overfit to the evolution tasks — a meaningful negative result
- [ ] **SC12:** Experiment produces a report with explicit generalization verdict and recommendation on whether to proceed to Experiment 2

---

## Resolved Design Decisions (Formerly Open Questions)

1. **Same tasks for baseline and evolved? → Yes, plus holdout set.** Same 5 evolution tasks run in baseline and all 3 evolved rounds — this enables per-task score trajectories across rounds. The overfitting risk is addressed by adding 3 frozen holdout tasks that are never seen during evolution. If evolution-set scores improve but holdout scores don't, the rules overfit. This was the strongest critique from the GPT 5.4 review and the holdout set directly addresses it.

2. **Consolidation context window → Current round only. Frozen for the entire experiment.** Each consolidation round sees only that round's 5 outputs + scores + the current rules. It does NOT see prior rounds' outputs. Rationale: keeps token cost predictable and prevents the consolidation loop from overfitting to early mistakes. **This protocol is frozen** — it does not change based on interim results. If round 2 doesn't improve over round 1, that is a valid experimental outcome to document, not a trigger to change the protocol in-place. If you want to test whether cumulative context helps, run it as a **separate follow-up experiment** after this one concludes.

3. **Judge model selection → Sonnet 4.6 judge, Opus 4.6 executor.** Different models for execution and judging to avoid self-grading bias. Judge runs at temperature 0.0 for deterministic scoring. Full config frozen in `scores/judge-config.json` before Phase 1 begins. Prompt hash (SHA-256) recorded to detect any accidental drift.

---

## Research Arc: From Consolidation to Cellular Division

This experiment (Phases 0-4) validates one component of the pattern @agentic.james described. The full arc toward self-organizing multi-agent systems requires four sequential experiments, each building on the findings of the previous one. **Do not begin a subsequent experiment until the prior experiment's report is complete and findings are positive.**

### Task Complexity Escalation Ladder

Each experiment escalates task complexity to ensure findings generalize beyond toy problems. If the consolidation loop only works on simple functions, it's an interesting result but not a useful tool.

| Experiment | Task Complexity | Example Tasks | Why This Level |
|---|---|---|---|
| **1: Backprop** | **Toy** — Single isolated utility functions. Clear right answers. Objectively scorable. | `slugify()`, `validate_email()`, `ttl_cache()` | Controlled environment to validate the mechanism works at all. Minimal confounding variables. |
| **2: Differentiation** | **Moderate** — Multi-concern tasks that span domains. Require trade-offs between competing quality dimensions. | "Build a CLI tool that fetches API data, validates it, caches results, and writes a report." "Create a data pipeline that reads CSV, cleans data, computes statistics, and outputs JSON." | Tasks must create **rule tension** to trigger agent division. Single-domain tasks won't expose the need for specialization. |
| **3: Topology** | **Complex** — Multi-file features with architectural decisions. Require coordination between components. | "Implement a webhook receiver with signature verification, event routing, retry queue, and dead letter handling." "Build a rate limiter with sliding window, per-user quotas, Redis backend, and admin override." | Tasks must be complex enough that review by a *specific* specialist matters. Generic review won't expose topology needs. |
| **4: Emergence** | **Production-scale** — Real tasks from your actual workflow. Ambiguous requirements, multi-session scope, architectural trade-offs. | Actual Claude Code tasks from your dev journal — feature implementations, refactoring, debugging sessions. | Emergence can only be validated against real work. Synthetic tasks have demand characteristics that bias toward prescribed behavior. |

**Why this ladder matters:** Experiment 1's toy tasks are deliberately simple so we can isolate whether the consolidation mechanism works. But "rules improve for `slugify()`" doesn't mean "rules improve for building a FastAPI service." Each subsequent experiment raises the bar. If the pattern breaks at a complexity level, that's the ceiling of the approach — and that's a valuable finding.

**The generalizability question is answered progressively:** Experiment 1 answers "does this work at all?" Experiment 2 answers "does this work when tasks require trade-offs?" Experiment 3 answers "does this work when coordination matters?" Experiment 4 answers "does this work on my real code?"

### Current Experiment (This Plan): Textual Backpropagation

**Question:** Do rules get measurably better when agents observe errors and edit behavioral files?
**Scope:** 1 task executor, 3 static support agents (critic/defender/synthesizer), prescribed consolidation schedule
**What you have at the end:** A single agent with evolved rules. No division. No emergent behavior. Proof (or disproof) that governed prompt-evolution under feedback improves output quality.
**Gate to next:** SC7 (evolved > baseline + 0.5) AND SC11 (holdout generalization > 0.3) must both pass. If SC7 passes but SC11 fails, the rules overfit — fix the consolidation loop's generalization before proceeding. If neither passes, the mechanism doesn't work at this complexity level.

---

### Experiment 2: Agent Differentiation (Cell Division)

**Question:** Can the consolidation loop detect when a single ruleset is insufficient and propose splitting into specialized agents?
**Prerequisite:** Experiment 1 report shows positive results (SC7 AND SC11 both passed — evolved scores improved AND holdout generalized)
**Research parallel:** Workflow autoconstruction (EvoAgentX), agent division in biological cells

**Task complexity: Moderate** (see Task Complexity Escalation Ladder above)

**Concept:**
- Start with one generic task executor and one unified ruleset
- Escalate to **moderate-complexity tasks** that span multiple domains (e.g., "Build a CLI tool that fetches API data, validates it, caches results, and writes a report"). These tasks deliberately create tension between competing concerns — I/O performance vs. validation thoroughness, caching efficiency vs. correctness
- Extend the synthesizer agent to detect **rule tension** — when optimizing for one quality dimension degrades another
- When tension is detected, the synthesizer proposes a **split**: fork the ruleset into two specialized variants (e.g., `io-specialist.md` and `algorithm-specialist.md`)
- A new **router agent** decides which specialist handles each task (or which parts of a task)

**Key design questions:**
- What triggers a split? Score variance across dimensions? Rule file size exceeding a threshold? Explicit conflict between rules?
- How does the router decide which specialist to invoke? Task analysis? Keyword matching? LLM classification?
- Can specialists be re-merged if the split didn't improve scores?
- What's the maximum number of specialists before the system becomes unmanageable?

**Mapping to Claude Code:**
- Each specialist = a separate rules directory (`rules/current/specialist-io/`, `rules/current/specialist-algo/`)
- Router = a lightweight sub-agent that reads the task spec and selects the specialist ruleset
- Division event = synthesizer writes a new specialist directory + router rules
- Project `CLAUDE.md` dynamically loads the selected specialist's rules

**Safety constraints (in addition to Experiment 1's):**
- Maximum 4 specialists (hard cap). Division beyond this is rejected
- Each division must be justified by a measurable quality delta — no speculative splits
- All specialists share a common base ruleset (`rules/current/shared.md`) to prevent total divergence
- Human approval required for every division event, not just rule edits

**Success criteria:**
- [ ] At least 1 meaningful split occurs (synthesizer detects rule tension and proposes division)
- [ ] Post-split scores exceed pre-split scores on the tensioned dimensions
- [ ] No dimension regresses by more than 1 point after a split
- [ ] Router correctly assigns tasks to specialists >80% of the time
- [ ] Total specialist count stays <= 4

---

### Experiment 3: Emergent Topology (Multi-Agent Review Networks)

**Question:** Can agents develop their own review relationships — deciding who reviews whom and how often?
**Prerequisite:** Experiment 2 report shows successful agent differentiation
**Research parallel:** HiVA Semantic-Topological Evolution (Tang et al.), AgentNet decentralized coordination (NeurIPS 2025), S-Agents self-organizing trees (Fudan)

**Task complexity: Complex** (see Task Complexity Escalation Ladder above)

**Concept:**
- Escalate to **complex multi-file tasks** with architectural decisions (e.g., "Implement a webhook receiver with signature verification, event routing, retry queue, and dead letter handling"). These tasks require coordination between components — a generic review won't catch the integration issues that a specialist reviewer would
- Multiple specialized agents (from Experiment 2) each have their own rulesets
- Introduce a **topology file** (`topology.md`) that defines review relationships: which agents review which others, and on what schedule
- The topology file is itself evolvable — the consolidation loop can propose changes to review structure, not just to behavioral rules
- Start with a simple topology (every agent reviewed by a single consolidator) and see if the system proposes a more complex structure

**What "emergent topology" means in Claude Code:**
- Today: you have a fixed set of sub-agent types (planner, reviewer, tdd-guide, etc.) with static relationships
- This experiment: agents can propose new review relationships ("the io-specialist should be reviewed by the algorithm-specialist because I/O correctness depends on algorithmic constraints")
- The topology file defines: reviewer → reviewee pairs, review frequency, review criteria
- The consolidation loop can add/remove/modify these pairs

**Key design questions:**
- Should topology changes require the same approval gate as rule changes, or a higher bar?
- How do you prevent circular reviews (A reviews B reviews A)?
- Is there a minimum viable topology below which the system degrades?
- How do you measure topology quality independent of rule quality?

**Safety constraints (in addition to prior experiments'):**
- Topology changes require explicit human approval (separate from rule change approval)
- No agent can review itself
- Maximum graph depth of 3 (no review chains longer than A → B → C → D)
- Cycle detection: reject any topology change that introduces a review cycle

**Success criteria:**
- [ ] System proposes at least 1 topology change (new review relationship)
- [ ] Topology change leads to measurable quality improvement in the reviewed agent
- [ ] No review cycles introduced
- [ ] System stabilizes to a consistent topology within 5 iterations (doesn't thrash)

---

### Experiment 4: Emergent Consolidation (Spontaneous Review Cycles)

**Question:** If agents are given the *ability* to request a review cycle but not the *instruction* to do so, will they spontaneously develop one?
**Prerequisite:** Experiment 3 report shows stable emergent topology
**Research parallel:** Ouroboros background consciousness loop (Razzhigaev, 2026), the original claim from @agentic.james's post

**This is the experiment that tests James's core claim:** that the 24-hour review cycle was *emergent*, not designed.

**Task complexity: Production-scale** (see Task Complexity Escalation Ladder above)

**Concept:**
- Escalate to **real tasks from your actual workflow** — feature implementations, refactoring, debugging sessions pulled from your dev journal. Synthetic tasks have demand characteristics that bias toward prescribed behavior; only real work can validate emergence
- Remove the prescribed consolidation schedule entirely
- Give each agent a **meta-instruction**: "You may request a system review at any time by writing a file to `consolidation/requests/`. Explain why you think a review is needed"
- Agents execute tasks normally. The system monitors the `requests/` directory
- If a request appears, the consolidation loop activates — but only because an agent asked for it
- Track: do agents request reviews? How often? Under what conditions? Does the frequency stabilize?

**Mapping to Claude Code:**
- Use a Claude Code hook (PostToolUse or Stop) to monitor `consolidation/requests/`
- When a request file appears, trigger the consolidation loop
- The meta-instruction lives in each agent's rules but says nothing about *when* to request — only *how*
- `/loop` skill could poll the requests directory on an interval as a detection mechanism

**What makes this the hardest experiment:**
- We're testing for emergent behavior, which by definition can't be prescribed
- The meta-instruction must be carefully worded: too suggestive and agents will always request reviews (demand characteristic). Too vague and they never will
- Need a long enough run (many tasks, multiple sessions) to observe patterns
- Single-session context limits may prevent agents from accumulating enough experience to recognize when a review is needed — may require the memory system for cross-session continuity

**Key design questions:**
- How do you distinguish "emergent review request" from "the agent is just following the meta-instruction literally"?
- What's the null hypothesis? How many requests would random chance produce?
- Does the agent need to experience failure before requesting a review, or will it request proactively?
- Can we run this without the memory system (single session) or does emergence require cross-session persistence?

**Safety constraints (in addition to all prior experiments'):**
- Same sandbox boundary — requests directory is inside the project
- Rate limit on review requests: maximum 1 per task cycle. Reject rapid-fire requests
- Budget ceiling increased to $100 (longer run expected)
- Automated kill switch if >10 requests in a single session (runaway loop detection)

**Success criteria:**
- [ ] At least 1 agent spontaneously requests a review without being explicitly told to
- [ ] Review requests correlate with actual quality issues (not random)
- [ ] A stable review cadence emerges (requests cluster around a consistent interval)
- [ ] Quality scores with emergent reviews match or exceed quality scores with prescribed reviews (Experiment 1)
- [ ] The system does NOT devolve into requesting reviews after every single task (that's not emergence, that's a fixed rule)

---

### Full Arc Dependency Graph

```
Experiment 1: Governed Prompt Evolution
  "Do evolved rules improve quality?"
  │
  │  Gate: SC7 (evolved > baseline + 0.5) AND SC11 (holdout generalizes + 0.3)
  ▼
Experiment 2: Agent Differentiation
  "Can one ruleset split into specialists?"
  │
  │  Gate: At least 1 successful split with quality improvement
  ▼
Experiment 3: Emergent Topology
  "Can agents develop their own review relationships?"
  │
  │  Gate: Stable topology emerges within 5 iterations
  ▼
Experiment 4: Emergent Consolidation
  "Will agents spontaneously request review cycles?"
  │
  │  Gate: Review requests correlate with quality issues
  ▼
  ┌──────────────────────────────────────────────────┐
  │  FULL VISION: Self-organizing multi-agent system  │
  │  that differentiates, self-reviews, and evolves   │
  │  — implemented entirely within Claude Code        │
  └──────────────────────────────────────────────────┘
```

**Each gate is a hard stop.** If an experiment fails to meet its success criteria, do not proceed to the next. Instead, iterate on the failing experiment until it passes or document why the approach doesn't work.

---

---
---

# Experiment 2: Agent Differentiation (Cell Division)

**Created:** 2026-03-20
**Status:** DRAFT — Awaiting Pilot Validation
**Prerequisite:** Experiment 1 complete (SC7 +1.58, SC11 +1.40 — both passed)
**Budget ceiling:** $300 (split arm) + $150 (control arm) = $450 total
**Reviewed by:** GPT 5.4 adversarial critique (2026-03-20), revisions incorporated

---

## Overview

Experiment 2 tests whether a governed consolidation loop can **propose structural forks** (specialist rulesets) when score patterns suggest persistent trade-offs — and whether those forks actually improve output quality beyond what continued generic evolution achieves.

The experiment uses a **two-arm design**: a split arm where agents can propose specialization, and a generic-only control arm with the same budget and rounds but no splits allowed. This isolates the specialization effect from the re-execution and continued-evolution effects that Experiment 1 could not cleanly separate.

Starting from Experiment 1's evolved rules (v2) as baseline, the experiment escalates to high-complexity multi-concern tasks that create genuine tension between competing quality dimensions. The hypothesis is that a single generic ruleset cannot optimize all dimensions simultaneously on these tasks, and that agent-proposed specialization will outperform continued generic evolution.

**Core question:** Does governed rule-forking into specialists — proposed by agents under fixed guardrails and human approval — produce better output quality than continued generic rule evolution on complex multi-concern tasks?

**Framing note:** "Cell division" is the motivating biological metaphor. The actual mechanism is governed rule-forking with inheritance, routing, and human approval. The experiment tests **endogenous specialization within a designed concern ontology**, not open-ended emergent self-organization.

---

## Resolved Design Decisions

### DD1: Two-Arm Design with Uniform Evolution Loop

**Decision:** Two parallel arms run on the same tasks for the same number of rounds:

- **Split arm:** Agents can propose rule edits, splits, further splits, or re-merges. Full structural freedom.
- **Control arm (generic-only):** Agents can propose rule edits only. Splits are forbidden. Same consolidation loop, same budget per round.

Both arms start from the same seed rules (Experiment 1 v2). The delta between arms isolates the specialization effect. Every evolution round in both arms runs the same loop.

**The evolution loop (runs every round):**
1. **Execute** all tasks with current rules (generic or specialist-routed)
2. **Judge** all outputs (6 core dimensions + 2 sub-dimensions)
3. **Detect tension** — compute cross-dimension variance per task
4. **Consolidate** — critic/defender/synthesizer debate, with tension data injected
5. **Synthesizer decides** one of:
   - **(a) Rule edits only** — normal evolution within current structure
   - **(b) Split proposal** — fork a ruleset into 2+ specialists (if currently generic, or sub-split an existing specialist)
   - **(c) Re-merge proposal** — collapse a failing specialist back into shared base
   - **(d) No change** — rules are converged, no action needed
6. **Human approval** — approves/rejects/modifies the proposal
7. **Apply** — update rules, router config, specialist directories as needed
8. **Checkpoint** — git commit, session logs

The system can go from 1 generic ruleset → 2 specialists → 4 specialists → re-merge back to 2 across successive rounds. The trajectory is agent-proposed and human-approved.

**Soft cap of 4 specialists.** The constraint is both outcome-based and task-count-grounded: every split must be justified by score evidence from 3+ tasks, every specialist must demonstrate improvement within 2 rounds or face re-merge, and no specialist can exist without sufficient routing volume (≥3 tasks across 2 rounds). With 8 evolution tasks, going beyond 4 specialists creates routing sparsity that makes evaluation unreliable — the cap is structural, not ideological.

**Why this matters:** The experiment tests whether agents can discover a *useful* number of specialists and self-correct when they overshoot, within the constraint that every specialist must be evaluable.

### DD2: Split Trigger Mechanism

**Decision:** Composite signal — quantitative tension detection + synthesizer judgment, with pre-registered axes and multi-round confirmation.

**Pre-registration:** Before the experiment begins (Phase 0), each task's primary and secondary concern axes are registered. This provides a ground-truth reference for whether observed tensions align with designed tensions or are noise.

After each round, `detect_tension.py` computes:
- **Cross-dimension score variance** per task (variance of the 6 dimension scores)
- **Tension signal:** fires if 3+ tasks show variance > 4.0 AND the high/low dimensions align with different pre-registered axes
- **Cluster analysis:** identifies which dimensions cluster together vs conflict
- **Repeatability check:** tension must persist across 2 consecutive rounds (not just 1) to qualify as a structural trigger. One-round spikes are classified as noise or underperformance, not trade-offs

This distinguishes:
- **Broad underperformance** (all dimensions low) — rule edits, not a split
- **Noisy judging** (one-round spike) — filtered by repeatability check
- **Repeatable trade-off** (same dimensions conflict across rounds and tasks) — split candidate

When the tension signal fires with multi-round confirmation, the synthesizer receives the dimension heatmap, cluster analysis, and the prompt: "Given this tension data, propose the best action: rule edits, a new split, a further split, or no change. Justify with score evidence."

The synthesizer can propose: initial split, further split, multi-way split, re-merge, or no change.

**Soft cap of 4 specialists** (see DD1). Every split must be justified with score evidence from 3+ tasks. Every specialist must beat the pre-split baseline by >= 0.3 on its targeted dimensions within 2 rounds (with ≥3 routed tasks across last 2 rounds), or face re-merge. Budget pressure and routing sparsity are the natural limits.

**Post-split counterfactual replay (preregistered selection):** After each split event, re-run the 2 tasks with the highest tension scores in the round that triggered the split under the old generic rules. Selection is mechanical (top-2 by tension score), not discretionary. This is cheap (2 extra executions) and provides direct evidence of whether the split itself helped.

### DD3: Task Design — High Complexity with Guaranteed Tension

**Decision:** 8 evolution tasks + 4 holdout tasks. Tasks are substantially harder than Experiment 1 — each produces a multi-file Python package (3-6 files, 300-600 lines) spanning 3+ concern domains with multiple tension axes.

**Why 8+4 instead of 6+3:** More tasks give the agents more signal to detect tension patterns. With only 6 tasks, a 3-way split would leave 2 tasks per specialist — too few for meaningful consolidation. With 8 tasks, even a 4-way split has 2 tasks per specialist minimum.

**Tension design principle:** Each task has a **primary tension** (the dominant trade-off) and **secondary tensions** (weaker cross-cutting concerns). This creates a rich tension landscape where the optimal number of specialists is not obvious — the agents must discover it.

**Concern domains (4 axes):**
- **I/O resilience** — error recovery, retry logic, streaming, cleanup, defensive file/network operations
- **Algorithmic precision** — type safety, mathematical correctness, immutability, pure functions, precise generics
- **API/interface design** — ergonomic interfaces, validation layers, documentation depth, configuration flexibility
- **Concurrency/safety** — thread safety, race condition prevention, resource lifecycle, deadlock avoidance

Each task spans 2-3 of these axes with a clear primary. A single ruleset optimizing for any one axis will degrade performance on tasks dominated by a different axis.

### DD4: Router Agent Design

**Decision:** LLM classification via Haiku 4.5, evolving alongside specialists.

- Input: Task spec + all current specialist profiles from `router-config.md`
- Output: `{"specialist": "...", "confidence": 0.85, "rationale": "..."}`
- Confidence < 0.6 → fallback to shared base (generic execution)
- Human reviews all router decisions for the first 2 rounds after any split event
- Router config evolves: when a new specialist is created, its profile is added; when one is merged, its profile is removed

**Multi-specialist routing:** If a task spans concerns covered by 2 specialists, the router picks the **primary** specialist based on the task's dominant tension axis. The router does NOT compose specialists (that's Experiment 3 territory).

**Router evaluation protocol:**
- **Gold label:** Each task's pre-registered primary axis defines the "correct" specialist. This is set before the experiment runs.
- **Abstention policy:** Confidence < 0.6 triggers generic fallback. Abstentions count against coverage (not accuracy). Report both: accuracy (of assignments made) and coverage (% of tasks assigned to a specialist).
- **Primary metric:** Downstream score utility — does routing to the assigned specialist produce higher scores than the generic fallback would? Measured via the post-split counterfactual replay.
- **Router and specialist quality are measured separately.** Router accuracy is measured against gold labels. Specialist quality is measured by score improvement vs generic. Both must pass independently.

### DD5: Specialist Ruleset Structure

**Decision:** Layered inheritance — shared base + N specialist overlays (no hard cap).

```
rules/exp2/vN/
  shared.md                     # Base rules ALL specialists inherit (max 80 lines)
  output-format.md              # Stays shared (no split)
  router-config.md              # Specialist profiles + classification prompt
  specialists/                  # Only exists after first split
    io-resilience/
      rules.md                  # I/O-specific rules (max 100 lines)
    algorithmic/
      rules.md                  # Algorithm-specific rules (max 100 lines)
    api-design/                 # Created if/when agents propose a 3rd specialist
      rules.md
    concurrency/                # Created if/when agents propose further specialists
      rules.md
    # ... additional specialists as agents see fit
```

**Before any split:** Rules use the Experiment 1 structure (task-executor.md, code-quality.md, output-format.md). At the first split, these are refactored into shared.md + specialist rules.

**Inheritance:** Specialist rules EXTEND the shared base. If a specialist rule conflicts with shared, the specialist wins — but the conflict must be documented with rationale.

**Line limits:** shared.md max 80 lines, each specialist max 100 lines, output-format.md max 30 lines. Total per-specialist context: ~210 lines max.

**Multi-specialist consolidation protocol (exact contract):**
- **Per round, per specialist:** One full debate (critic/defender/synthesizer) scoped to that specialist's routed tasks and scores. Each debate sees: the specialist's rules, the shared base, the specialist's task outputs + scores, and the tension heatmap. It does NOT see other specialists' rules or outputs.
- **Shared-base changes:** Any specialist's synthesizer can propose changes to shared.md. Shared-base proposals are collected from all specialist debates, then a **consensus round** runs: a single synthesizer receives all shared-base proposals and resolves conflicts. If two specialists want contradictory shared-base changes, the consensus synthesizer picks one or rejects both.
- **Debate count per round:** 1 debate per active specialist + 1 consensus debate for shared base = N+1 debates total.
- **Split/merge proposals:** Only the specialist-scoped synthesizer can propose a further split of its own domain. Only the consensus synthesizer can propose a cross-specialist merge.
- **All proposals go to human approval.** The human sees the full picture (all specialist debates + consensus) before approving.

### DD6: Re-Merge Criteria

**Decision:** A specialist is a re-merge candidate if it meets ALL of:
1. Scores do not exceed pre-split baseline by >= 0.3 on targeted dimensions for 2 consecutive rounds
2. The specialist has been routed at least 3 tasks across the last 2 rounds combined (rolling threshold — avoids noisy decisions from single-round routing variance)
3. At least 1 counterfactual comparison exists (same task run under generic rules for comparison)

If a specialist has been routed fewer than 3 tasks across 2 rounds, it is automatically a re-merge candidate — insufficient routing volume means the specialist is not earning its structural cost.

Re-merge can also be **proactive**: if the synthesizer observes that two specialists' rules have converged (>80% overlap), it can propose merging them into one.

If ALL specialists fail re-merge criteria: the experiment concludes with a valid negative result.

### DD7: Judge Rubric

**Decision:** Keep Experiment 1's 6 core dimensions as the primary metric. Add 2 sub-dimensions scored separately (NOT in overall score):
- **Architecture** — module structure, separation of concerns, interface design
- **Integration coherence** — do components work together, clean inter-module interfaces

Sub-dimensions inform consolidation but don't affect the primary metric, preserving cross-experiment comparability.

**Sub-dimension guardrail:** Architecture and integration_coherence must not regress by more than 1.0 point from baseline in any round. On multi-file systems tasks, structural quality is not a side issue — a specialist that improves code_quality but tanks architecture is not a real improvement. If a round violates this guardrail, the consolidation loop must address it before proceeding.

### DD8: Round Structure — Uniform Evolution Loop (Both Arms)

**Decision:** Both arms run the same structure: 1 baseline round + 5 evolution rounds + 1 holdout round.

| Round | Split Arm | Control Arm |
|-------|-----------|-------------|
| R0 | Baseline — 10 tasks, seed rules, judge, tension detect | Same (shared baseline) |
| R1 | Evolution — edits/split/merge allowed | Evolution — edits only |
| R2 | Evolution — same | Evolution — edits only |
| R3 | Evolution — same | Evolution — edits only |
| R4 | Evolution — same | Evolution — edits only |
| R5 | Evolution — convergence expected | Evolution — convergence expected |
| H1 | Holdout — 4 tasks with final rules | Holdout — 4 tasks with final rules |

**Why 5 evolution rounds:**
- Experiment 1 converged in 2-3 rounds on simple tasks
- Complex tasks with iterative splitting need more rounds for the full differentiation arc
- A plausible split-arm trajectory: R1-R2 generic evolution → R3 first split → R4-R5 specialist evolution + convergence
- 5 rounds keeps the unmitigated budget estimate under the ceiling without relying on aspirational mitigations
- But the agents might split at R1, or never split — the trajectory is not prescribed

**Early termination:** If agents in either arm propose "no change" for 2 consecutive rounds AND no tension signal fires, that arm's evolution is converged. Skip remaining rounds for that arm.

**Task count:** 10 tasks per round (8 evolution + 2 negative-control tasks that should NOT benefit from splitting — see DD10).

**Execution totals (authoritative):**

| Category | Split Arm | Control Arm | Total |
|----------|-----------|-------------|-------|
| Baseline (R0, shared) | 10 tasks | — | 10 |
| Evolution (R1-R5) | 5 × 10 = 50 | 5 × 10 = 50 | 100 |
| Post-split counterfactual replays | ~4-6 (est.) | 0 | ~5 |
| Holdout pre (shared baseline) | 4 tasks | — | 4 |
| Holdout post | 4 | 4 | 8 |
| Executor variance calibration (pilot) | 4 | — | 4 |
| **Total** | **~72** | **~58** | **~131** |

### DD9: Budget (Both Arms)

| Category | Split Arm | Control Arm | Total |
|----------|-----------|-------------|-------|
| Executions (Opus, $2-4 each) | ~66 × $3 = $198 | ~56 × $3 = $168 | $366 |
| Judge calls (Sonnet, 3x then 2x) | ~$18 | ~$15 | $33 |
| Consolidation (3 agents/round) | 5 × $10 = $50 | 5 × $8 = $40 | $90 |
| Router (Haiku) | ~$1 | $0 | $1 |
| **Total estimate** | **~$267** | **~$223** | **~$490** |

This is high. **Budget ceiling: $450 total** with these mitigations:
- Early termination on convergence (saves 2-3 rounds per arm = $60-120)
- Reduce judge to 2x median after R2 if inter-run variance is low (saves ~$15)
- If no tension after R3 in split arm, conclude early (saves ~$80)
- **Realistic expected spend: $300-400**

**Mandatory budget-cut sequence** (triggered in order if spend exceeds checkpoints):
1. At $250 spent: Reduce judge to 2x median for remaining rounds (if not already)
2. At $300 spent: Drop to 1x judge calls for rounds where inter-run variance < 0.5
3. At $350 spent: Cap remaining rounds at 1 more per arm (finish current + 1)
4. At $400 spent: Complete current round only, then proceed to holdout evaluation

**Both arms use the same executor model (Opus) throughout.** No model downgrade on either arm — differing models would confound the specialization comparison.

### DD10: Negative-Control Tasks

**Decision:** Add 2 tasks to the evolution set that have **no designed tension** — single-concern tasks where a generic ruleset should perform as well as any specialist. These tasks test whether the system correctly avoids splitting when splitting isn't warranted.

If the agents propose splitting on these tasks, that's a signal of overzealous splitting. If the agents correctly leave these tasks on the generic/shared path, that validates the tension detection mechanism.

These 2 tasks are included in every round for both arms. They are scored normally but flagged in analysis as negative controls.


---

## Task Specifications

### Evolution Tasks (8 tasks)

Tasks are organized by primary concern domain but each spans 2-3 domains. This ensures that any single-axis specialist still faces cross-cutting tension, incentivizing further splits or nuanced shared rules.

#### E2-001: ETL Pipeline with Schema Validation and Error Recovery
**Primary:** I/O resilience | **Secondary:** Algorithmic precision, API design
Build a multi-source ETL pipeline that: reads from CSV/JSON/TOML files, validates each record against a typed schema (with coercion rules), quarantines invalid records with structured error reports, computes aggregate statistics on valid data, and writes output to multiple formats. Must handle: corrupted files, encoding issues, partial reads, memory-efficient streaming for large files.
**Files:** `pipeline.py`, `schema.py`, `validators.py`, `writers.py`, `test_pipeline.py`
**Expected output:** 400-600 lines across 5 files

#### E2-002: HTTP Client with Retry, Circuit Breaker, Cache, and Rate Limiting
**Primary:** I/O resilience | **Secondary:** Concurrency/safety, API design
HTTP client wrapper with: exponential backoff + jitter retry, circuit breaker pattern (open/half-open/closed), per-domain TTL cache with stale-while-revalidate, token bucket rate limiter, request/response middleware hooks, structured error taxonomy. `urllib` only. Thread-safe for concurrent use.
**Files:** `client.py`, `circuit_breaker.py`, `cache.py`, `rate_limiter.py`, `middleware.py`, `test_client.py`
**Expected output:** 500-600 lines across 6 files

#### E2-003: Expression Evaluator with Type System and Error Reporting
**Primary:** Algorithmic precision | **Secondary:** API design, I/O resilience
Build a safe expression evaluator that: parses a mini-language (arithmetic, string ops, comparisons, ternary, variable references), type-checks expressions before evaluation, supports user-defined variables with type declarations, produces source-mapped error messages with line/column info, and handles: nested expressions, operator precedence, type coercion rules, division by zero, undefined variables.
**Files:** `lexer.py`, `parser.py`, `type_checker.py`, `evaluator.py`, `errors.py`, `test_evaluator.py`
**Expected output:** 500-600 lines across 6 files

#### E2-004: B-Tree Index with Disk Persistence and Range Queries
**Primary:** Algorithmic precision | **Secondary:** I/O resilience, Concurrency/safety
Implement a B-tree index that: supports insert/delete/search/range-query operations, persists to disk with page-based storage, handles concurrent reads (single writer), supports configurable branching factor, provides iterator interface for range scans, and maintains invariants under crash recovery (write-ahead log).
**Files:** `btree.py`, `page_store.py`, `wal.py`, `iterator.py`, `test_btree.py`
**Expected output:** 500-600 lines across 5 files

#### E2-005: Plugin System with Dependency Resolution and Lifecycle Management
**Primary:** API design | **Secondary:** Algorithmic precision, Concurrency/safety
Build a plugin framework that: discovers plugins from a directory, resolves dependency graphs (with cycle detection), manages plugin lifecycle (init → configure → start → stop → destroy), supports configuration injection via typed schemas, provides a hook/event system for inter-plugin communication, and handles: missing dependencies, version conflicts, startup failures with partial rollback.
**Files:** `registry.py`, `resolver.py`, `lifecycle.py`, `hooks.py`, `config.py`, `test_plugin_system.py`
**Expected output:** 500-600 lines across 6 files

#### E2-006: CLI Framework with Subcommands, Config Layers, and Shell Completion
**Primary:** API design | **Secondary:** I/O resilience, Algorithmic precision
Build a CLI framework that: supports nested subcommands with help generation, merges config from 4 layers (CLI args > env vars > config file > defaults), generates shell completion scripts (bash/zsh), validates all inputs with typed schemas, provides colored output and progress bars, and handles: unknown arguments gracefully, config file parse errors, terminal capability detection.
**Files:** `cli.py`, `config_merger.py`, `completion.py`, `output.py`, `test_cli.py`
**Expected output:** 400-500 lines across 5 files

#### E2-007: Actor-Based Task Scheduler with Supervision and Backpressure
**Primary:** Concurrency/safety | **Secondary:** I/O resilience, API design
Build an actor-model task scheduler that: manages a hierarchy of actors (supervisor → workers), routes messages between actors via typed mailboxes, implements supervision strategies (one-for-one, all-for-one restart), supports backpressure (mailbox limits with configurable overflow policy), provides graceful shutdown with drain timeout, and handles: actor crashes, message delivery failures, supervisor cascade failures.
**Files:** `actor.py`, `mailbox.py`, `supervisor.py`, `scheduler.py`, `test_scheduler.py`
**Expected output:** 500-600 lines across 5 files

#### E2-008: Distributed Lock Manager with Fencing and Deadlock Detection
**Primary:** Concurrency/safety | **Secondary:** Algorithmic precision, I/O resilience
Build an in-process distributed lock manager that: supports exclusive and shared locks, implements fencing tokens for lock safety, detects deadlocks via wait-for graph analysis, supports lock timeouts with automatic release, provides lock upgrade/downgrade (shared → exclusive), and handles: holder crashes (lease expiry), lock contention metrics, priority inversion prevention.
**Files:** `lock_manager.py`, `fencing.py`, `deadlock_detector.py`, `metrics.py`, `test_lock_manager.py`
**Expected output:** 400-500 lines across 5 files

### Holdout Tasks (4 tasks)

Holdout tasks span all 4 concern domains. They are never seen during evolution or consolidation.

#### H2-001: Event Sourcing Store with Snapshots and Projections
**Tensions:** I/O resilience + Algorithmic precision + API design
Event store with append-only log, snapshot compaction, configurable projections, replay from any point, and concurrent read access.

#### H2-002: Constraint Solver with Backtracking and Explanation
**Tensions:** Algorithmic precision + API design + Concurrency/safety
CSP solver with arc consistency, chronological backtracking, conflict-driven learning, solution enumeration, and constraint violation explanations.

#### H2-003: Service Mesh Sidecar with Load Balancing and Health Propagation
**Tensions:** Concurrency/safety + I/O resilience + API design
In-process sidecar with round-robin/least-connections/weighted load balancing, health check propagation, circuit breaking per upstream, request hedging, and graceful degradation.

#### H2-004: Schema Registry with Compatibility Checking and Migration Paths
**Tensions:** API design + Algorithmic precision + I/O resilience
Schema registry supporting JSON Schema and Avro, backward/forward/full compatibility checking, migration path generation between versions, and persistent storage with caching.

### Negative-Control Tasks (2 tasks — no designed tension)

These tasks are single-concern, high-quality tasks where a generic ruleset should perform well. They test whether the system correctly avoids unnecessary specialization.

#### NC-001: Markdown Table Formatter
**Concern:** Algorithmic precision only
Pure function that parses markdown tables, normalizes column widths, aligns content, handles multi-line cells, and outputs formatted markdown. No I/O, no concurrency, no API design complexity. A generic code-quality ruleset should ace this.
**Files:** `formatter.py`, `test_formatter.py`
**Expected output:** 150-250 lines across 2 files

#### NC-002: JSON Patch Implementation (RFC 6902)
**Concern:** Algorithmic precision only
Implement JSON Patch operations (add, remove, replace, move, copy, test) per RFC 6902. Pure data transformation, well-specified by the RFC, no I/O or concurrency. Should not benefit from specialization.
**Files:** `json_patch.py`, `test_json_patch.py`
**Expected output:** 200-300 lines across 2 files

---

## Human Intervention Protocol

Every human approval decision is logged with a classification:

| Type | Definition |
|------|-----------|
| **approve-unchanged** | Proposal accepted as-is |
| **reject** | Proposal rejected entirely |
| **edit-light** | Minor wording/scoping change, preserves intent |
| **edit-heavy** | Substantial modification to proposal structure or content |

The analysis phase (Phase 4) will correlate intervention types with score outcomes to separate agent-originated progress from human-shaped progress. If >30% of approvals are edit-heavy, the experiment's "agent-driven" claim is weakened and this must be reported.

---

## New Infrastructure

### New Scripts (TDD)
1. `scripts/detect_tension.py` — Cross-dimension variance, cluster analysis, tension signal
2. `scripts/route_task.py` — Haiku-based task-to-specialist classification
3. `scripts/split_rules.py` — Create/extend specialist directories from split proposal
4. `scripts/merge_specialist.py` — Re-merge failed specialist into shared base

### Extended Scripts
5. `scripts/consolidate.py` — Add `--mode adaptive` for agent-driven split/merge/edit decisions + tension heatmap injection
6. `scripts/apply_rules.py` — Support specialist directory structure (dynamic count)
7. `scripts/judge.py` — Add `--sub-dimensions` for architecture + integration_coherence

### New Agent Prompts
8. `consolidation/exp2/tension-detector-prompt.md` — Heatmap + cluster analysis for synthesizer
9. `consolidation/exp2/adaptive-synthesizer-prompt.md` — Unified prompt for edit/split/merge/no-change decisions
10. `consolidation/exp2/router-prompt.md` — Task classification to specialist
11. `consolidation/exp2/specialist-consolidation-prompt.md` — Per-specialist evolution scoped to one domain

---

## Phase 0: Experiment 2 Setup

**Goal:** Directory structure, task specs, acceptance tests, infrastructure extensions, pilot validation.
**Dependency:** Experiment 1 complete

### Experiment 1 File Reorganization

Move all Experiment 1 artifacts under `exp1/` subdirectories so experiments don't collide. This is a one-time migration before Experiment 2 begins.

**Current → New mapping:**
```
rules/v0/, v1/, v2/, current      → rules/exp1/v0/, v1/, v2/, current
outputs/baseline/, evolved/       → outputs/exp1/baseline/, evolved/
scores/baseline/, evolved/, holdout-pre/  → scores/exp1/baseline/, evolved/, holdout-pre/
tasks/acceptance/, task-*.md      → tasks/exp1/acceptance/, task-*.md
holdout/acceptance/, outputs/, specs/  → holdout/exp1/acceptance/, outputs/, specs/
consolidation/applied/, approvals/, debates/, proposals/  → consolidation/exp1/applied/, approvals/, debates/, proposals/
```

- [ ] **0.0pre-a** Create `exp1/` subdirectories under each top-level data dir
- [ ] **0.0pre-b** Move Experiment 1 artifacts into `exp1/` subdirs (git mv to preserve history)
- [ ] **0.0pre-c** Update `rules/exp1/current` symlink: `current -> v2`
- [ ] **0.0pre-d** Update `scripts/judge.py`, `scripts/consolidate.py`, `scripts/apply_rules.py` — any hardcoded paths to old locations
- [ ] **0.0pre-e** Update `CLAUDE.md` project structure section for new layout
- [ ] **0.0pre-f** Run existing tests to confirm nothing broke: `pytest tasks/exp1/acceptance/ -v`
- [ ] **0.0pre-g** Git commit: `chore: reorganize exp1 files under exp1/ subdirectories`

**Post-migration structure:**
```
rules/exp1/v0/, v1/, v2/, current    # Experiment 1 rules (frozen)
rules/exp2/v0/, current              # Experiment 2 rules (active)
outputs/exp1/baseline/, evolved/     # Experiment 1 outputs (frozen)
outputs/exp2/baseline/, split/, control/  # Experiment 2 outputs (active)
scores/exp1/...                      # Experiment 1 scores (frozen)
scores/exp2/...                      # Experiment 2 scores (active)
tasks/exp1/...                       # Experiment 1 tasks (frozen)
tasks/exp2/...                       # Experiment 2 tasks (active)
holdout/exp1/...                     # Experiment 1 holdout (frozen)
holdout/exp2/...                     # Experiment 2 holdout (active)
consolidation/exp1/...               # Experiment 1 consolidation (frozen)
consolidation/exp2/...               # Experiment 2 consolidation (active)
```

### Preflight Checklist
- [ ] **0.0a** Verify git repo operational (branches, worktrees, commits)
- [ ] **0.0b** Verify session logging captures all invocation types
- [ ] **0.0c** Verify cost tracking is live and accurate
- [ ] **0.0d** Verify holdout isolation: `holdout/exp2/` excluded from executor workspace
- [ ] **0.0e** Verify worktree flow works (create, execute, merge, cleanup)
- [ ] **0.0f** Verify Experiment 1 reorganization complete (all `exp1/` paths resolve, no stale top-level artifacts)

### Setup
- [ ] **0.1** Create Experiment 2 directory structure: `tasks/exp2/`, `holdout/exp2/`, `outputs/exp2/`, `scores/exp2/`, `consolidation/exp2/`, `rules/exp2/v0/`, `rules/exp2/current -> v0/`, `holdout/exp2/sealed/` (for sealed pre-scores)
- [ ] **0.2** Copy Experiment 1's v2 rules from `rules/exp1/v2/` to `rules/exp2/v0/` as seed baseline
- [ ] **0.3** Write 8 evolution task specs (`tasks/exp2/task-E2-001.md` through `E2-008.md`) with: full requirements, edge cases, expected file structure, **pre-registered primary and secondary concern axes**
- [ ] **0.4** Write 2 negative-control task specs (`tasks/exp2/task-NC-001.md`, `NC-002.md`) — single-concern, no designed tension
- [ ] **0.5** Write 4 holdout task specs (`holdout/exp2/specs/holdout-H2-001.md` through `H2-004.md`)
- [ ] **0.6** `/steadows-tdd` — Tiered test suite for all 14 tasks:
  - **Acceptance tests** for core behavior (15-25 per task)
  - **Property tests** for algorithmic invariants (where applicable)
  - **Stress tests** for concurrency/resilience tasks (thread safety, crash recovery)
- [ ] **0.7** Write judge rubric addendum (`scores/exp2/judge-rubric-addendum.md`) with sub-dimensions + regression guardrail
- [ ] **0.8** Extend `scripts/judge.py` with `--sub-dimensions` flag

### Pilot Validation (4 tasks, expanded)
- [ ] **0.9** **Pilot execution:** Execute E2-001 (I/O), E2-003 (algorithmic), E2-005 (API), E2-007 (concurrency) — one per axis — with seed rules
- [ ] **0.10** Judge all 4 pilot outputs. Compute cross-dimension variance per task
- [ ] **0.11** **Executor variance measurement:** Re-execute E2-001 and E2-003 a second time with identical rules. Compare scores across the 2 runs. If executor variance > 1.0 on any dimension, the effect size threshold may need raising
- [ ] **0.12** **Freeze tension thresholds:** Based on pilot data, confirm or adjust the tension signal threshold (target: variance > 4.0 on 3+ tasks). If pilot variance is < 2.0 across all tasks, redesign tasks before proceeding
- [ ] **0.13** **Validate difficulty:** If pilot baseline scores are > 9.0 average, tasks are too easy — redesign before proceeding. If scores are < 5.0 average, tasks are too hard — simplify

### Infrastructure
- [ ] **0.14** `/steadows-tdd` — `scripts/detect_tension.py` (variance + cluster analysis + repeatability check)
- [ ] **0.15** `/steadows-tdd` — `scripts/route_task.py`
- [ ] **0.16** `/steadows-tdd` — `scripts/split_rules.py` (create + extend specialist dirs, rollback)
- [ ] **0.17** `/steadows-tdd` — `scripts/merge_specialist.py`
- [ ] **0.18** Extend `scripts/consolidate.py` with `--mode adaptive` + `--mode generic-only` (for control arm)
- [ ] **0.19** Extend `scripts/apply_rules.py` for specialist directory structure (dynamic count)
- [ ] **0.20** Write all new agent prompts (tension-detector, adaptive-synthesizer, router, specialist-consolidation, consensus)
- [ ] **0.21** Write Experiment 2 approval rubric (`consolidation/exp2/approval-rubric.md`) — covers rule edits, split proposals, further splits, re-merges, with human intervention type logging
- [ ] **0.22** Update project `CLAUDE.md` for Experiment 2 structure and isolation
- [ ] **0.23** `/steadows-verify` — Phase 0 gate

## Phase 1: Baseline (Shared Between Arms)

**Goal:** Execute all 14 tasks (8 evolution + 2 negative-control + 4 holdout) with seed rules. Establish control measurement and initial tension profile. This baseline is shared between both arms.
**Dependency:** Phase 0 complete

- [ ] **1.1** Execute E2-001 through E2-008 + NC-001, NC-002 with exp2/v0 rules → `outputs/exp2/baseline/`
- [ ] **1.2** Run acceptance tests against all 10 outputs
- [ ] **1.3** Judge all 10 outputs (3x median, including sub-dimensions)
- [ ] **1.4** Run `detect_tension.py` — record baseline tension profile (this is the pre-evolution measurement)
- [ ] **1.5** Holdout pre-evaluation (isolated worktree): H2-001 through H2-004 with exp2/v0 rules
- [ ] **1.6** Judge holdout outputs. **Seal holdout pre-scores** into `holdout/exp2/sealed/` — these scores are NOT accessible to the consolidation workflow until the experiment ends. Do not merge holdout worktree artifacts into the main workspace
- [ ] **1.7** Compile evolution + negative-control scores → `scores/exp2/baseline-scores.json`
- [ ] **1.8** Git checkpoint: `data: exp2 baseline scores`
- [ ] **1.9** `/steadows-verify` — Phase 1 gate: all outputs exist, all scores recorded, tension profile documented, holdout pre-scores sealed

## Phase 2: Evolution Loop (5 rounds × 2 arms)

**Goal:** Run both arms in parallel. Split arm: agents can propose rule edits, splits, merges. Control arm: agents can only propose rule edits (no structural changes). Both arms run on the same 10 tasks per round.
**Dependency:** Phase 1 complete

**Context management:** Each round should start in a **fresh session**. Load context from the latest snapshot in `.context/snapshots/`. **All task execution MUST use subagents (Agent tool)** — never run tasks directly in the main session. This keeps task outputs out of the orchestrating context window. Take a `/steadows-checkpoint` snapshot at the end of each round before context reset. With 2 arms × 10 tasks per round, context will fill fast without this discipline.

### Per-Round Protocol (repeats for R1–R5, each arm independently)

For round N in each arm:
1. **Execute** — Route (if specialists exist, split arm only) and execute all 10 tasks (8 evolution + 2 negative-control) with current rules → `outputs/exp2/{arm}/round-0N/`
2. **Test + Judge** — Acceptance tests + judge all 10 outputs (3x median through R2, then 2x median if inter-run variance is low)
3. **Detect tension** — `detect_tension.py` on round scores
4. **Consolidate** — Run consolidation loop:
   - **Split arm:** If specialists exist: per-specialist debate + shared-base consensus (N+1 debates). If generic: standard critic/defender/synthesizer. Tension data injected. Synthesizer can propose: **(a) rule edits, (b) split, (c) further split, (d) re-merge, (e) no change**
   - **Control arm:** Standard critic/defender/synthesizer. Splits forbidden. Synthesizer can only propose: **(a) rule edits or (e) no change**
   - **Asymmetry note:** The split arm may run more consolidation debates (N+1 vs 1) once specialists exist. This is inherent to the treatment — specialization includes the cost of coordinating specialists. The budget table accounts for this. Analysis should note this as a confound in the deliberation-time dimension.
5. **Human approval** — Review and approve/reject/modify. **Log intervention type** (approve-unchanged / reject / edit-light / edit-heavy)
6. **Apply** — Update rules (and specialist dirs/router config in split arm) → exp2/{arm}/vN
7. **Post-split counterfactual** (split arm only, when a split occurred this round): Re-execute the 2 tasks with the highest tension scores from the triggering round under the pre-split generic rules. Selection is mechanical (top-2 by tension score), not discretionary. Compare scores to the new specialist execution. Log as counterfactual evidence.
8. **Checkpoint** — Git commit, session logs, budget check

### Round Tasks (each arm)

#### Round 1
- [ ] **2.1a** [split] Execute 10 tasks with exp2/split/v0 → `outputs/exp2/split/round-01/`
- [ ] **2.1b** [control] Execute 10 tasks with exp2/control/v0 → `outputs/exp2/control/round-01/`
- [ ] **2.2** Tests + judge both arms
- [ ] **2.3** Tension detection both arms
- [ ] **2.4** Consolidation: split arm (adaptive) + control arm (generic-only)
- [ ] **2.5** Human approval (both arms) → apply → v1

#### Round 2
- [ ] **2.6a/b** Execute both arms with v1 → round-02/
- [ ] **2.7** Tests + judge + tension + consolidation + approval → v2

#### Round 3
- [ ] **2.8a/b** Execute both arms with v2 → round-03/
- [ ] **2.9** Tests + judge + tension + consolidation + approval → v3
- [ ] **2.9c** **Budget checkpoint:** Trigger mandatory budget-cut sequence per DD9 thresholds

#### Round 4
- [ ] **2.10a/b** Execute both arms with v3 → round-04/
- [ ] **2.11** Tests + judge + tension + consolidation + approval → v4

#### Round 5
- [ ] **2.12a/b** Execute both arms with v4 → round-05/
- [ ] **2.13** Tests + judge + tension + consolidation + approval → v5
- [ ] **2.13c** **Budget checkpoint**

**Early termination (per arm):** If agents propose "no change" for 2 consecutive rounds AND no tension signal fires, that arm is converged. Skip remaining rounds for that arm. Early termination is a valid completion state — it does not invalidate the arm's results. The primary comparison (SC-O1) uses each arm's final state regardless of how many rounds it took to reach it.

- [ ] **2.14** `/steadows-verify` — Phase 2 gate (all rounds complete or early termination documented for both arms)

### Differentiation Event Log (split arm)

Track every structural change in `consolidation/exp2/differentiation-log.md`:

```
| Round | Action | Detail | Specialist Count | Human Intervention |
|-------|--------|--------|-----------------|-------------------|
| R1 | rule edits | Updated shared code-quality | 1 (generic) | approve-unchanged |
| R3 | split | io-resilience + algorithmic | 2 | approve-unchanged |
| R3 | counterfactual | E2-001, E2-004 re-run under generic | — | — |
| R4 | further split | api-design from algorithmic | 3 | edit-light |
| R5 | no change | converged | 3 | approve-unchanged |
```

This log + the control arm's score trajectory are the primary artifacts for causal attribution.

## Phase 3: Holdout Evaluation (Both Arms)

**Goal:** Test final rules from both arms on unseen holdout tasks. Unseal pre-scores for comparison.
**Dependency:** Phase 2 complete

- [ ] **3.1** [split arm] Holdout post-evaluation worktree with final split-arm rules
- [ ] **3.2** Route H2-001–004 via router (if specialists exist) → assign
- [ ] **3.3** Execute with assigned specialist/generic rules → `outputs/exp2/split/holdout-post/`
- [ ] **3.4** [control arm] Holdout post-evaluation worktree with final control-arm rules
- [ ] **3.5** Execute with control-arm generic rules → `outputs/exp2/control/holdout-post/`
- [ ] **3.6** Acceptance tests + judge all 8 holdout outputs (4 per arm, including sub-dimensions)
- [ ] **3.7** **Unseal holdout pre-scores** from `holdout/exp2/sealed/` — now compare pre vs post for both arms
- [ ] **3.8** Compile → `scores/exp2/holdout-scores.json` (both arms + pre)
- [ ] **3.9** `/steadows-verify` — Phase 3 gate

## Phase 4: Analysis and Report

**Goal:** Comprehensive analysis of agent-driven differentiation.
**Dependency:** Phase 3 complete

- [ ] **4.1** **Split arm vs control arm comparison** — the primary result. Did the split arm outperform the control arm? By how much? On which dimensions? This isolates the specialization effect from continued-evolution effect
- [ ] **4.2** Score trajectories: baseline → per-round evolution for both arms → holdout
- [ ] **4.3** Differentiation analysis: when did splits occur? what triggered them? how many specialists emerged? did the agents self-correct (split then merge)?
- [ ] **4.4** Counterfactual replay analysis: at each split event, did the specialist rules beat the generic rules on the replayed tasks?
- [ ] **4.5** Tension resolution: did splits reduce cross-dimension variance on targeted axes?
- [ ] **4.6** Router accuracy analysis — accuracy vs gold labels, coverage, downstream score utility
- [ ] **4.7** Negative-control analysis: did agents correctly avoid splitting on NC-001/NC-002?
- [ ] **4.7b** Holdout oracle-routing sensitivity analysis: re-score holdout tasks using hand-assigned "correct" specialist routing to separate router error from specialist failure
- [ ] **4.8** Specialist convergence: how did each specialist's rules evolve independently?
- [ ] **4.9** Holdout generalization: both arms vs sealed pre-scores
- [ ] **4.10** Human intervention analysis: breakdown by type (approve-unchanged/reject/edit-light/edit-heavy), correlation with score outcomes, % agent-originated vs human-shaped progress
- [ ] **4.11** Cross-experiment comparison (Exp1 vs Exp2)
- [ ] **4.12** Cost analysis from session-logs (both arms)
- [ ] **4.13** Drift analysis (`analysis/exp2/drift-analysis.md`)
- [ ] **4.14** Convergence analysis (`analysis/exp2/convergence.md`)
- [ ] **4.15** Final report (`analysis/exp2/report.md`) — hypothesis, methodology (including two-arm design), results (including differentiation trajectory + causal attribution), limitations, Experiment 3 recommendation. Use "governed specialization" framing, not "autonomous emergence"
- [ ] **4.16** Dev journal entry
- [ ] **4.17** Git checkpoint: `docs: exp2 analysis complete`
- [ ] **4.18** `/steadows-verify` — Phase 4 gate (final)

---

## Experiment 2 Success Criteria

### Execution Criteria
- [ ] **SC-E1:** Both arms complete all rounds with valid scores (or early termination documented per arm)
- [ ] **SC-E2:** At least 3 evolution rounds completed per arm (early termination after 3+ rounds with documented convergence criteria is valid)
- [ ] **SC-E3:** Total cost under $450 (both arms combined)
- [ ] **SC-E4:** All rules git-versioned, within line limits, no sandbox violations
- [ ] **SC-E5:** All approval decisions (edits + splits + merges) recorded with rationale and intervention type
- [ ] **SC-E6:** Session metadata logged for every paid invocation (both arms)
- [ ] **SC-E7:** Differentiation event log complete (split arm)
- [ ] **SC-E8:** Human intervention breakdown logged for every approval (approve-unchanged / reject / edit-light / edit-heavy)

### Outcome Criteria (Two-Arm Comparison)
- [ ] **SC-O1:** Split arm final-state mean exceeds control arm final-state mean, where "final state" is each arm's rules at convergence or R5, whichever comes first (specialization beat generic evolution)
- [ ] **SC-O2:** At least 1 agent-initiated split occurs in the split arm, backed by score evidence from 3+ tasks with multi-round confirmed tension
- [ ] **SC-O3:** Post-split counterfactual replays show specialist scores > generic scores on replayed tasks
- [ ] **SC-O4:** No dimension regresses by > 1.0 after any structural change; architecture/integration sub-dimensions do not regress > 1.0 from baseline
- [ ] **SC-O5:** Router assigns correctly >80% vs gold labels (if specialists exist), with coverage reported separately
- [ ] **SC-O6:** Every specialist that persists to the final round demonstrates >= 0.3 improvement on its targeted dimensions (no dead-weight specialists)
- [ ] **SC-O7:** Split arm holdout post > holdout pre by >= 0.3 (generalization)
- [ ] **SC-O8:** Split arm holdout post >= control arm holdout post (specialist rules generalize better than generic rules)
- [ ] **SC-O9:** Negative-control tasks (NC-001, NC-002) are never the primary justification for a split proposal — agents correctly avoid specialization when it isn't warranted. Operationally: no split proposal cites NC tasks as evidence, and if NC tasks are routed to a specialist, their scores do not exceed their generic-rules scores by ≥0.3
- [ ] **SC-O10:** <30% of human approvals are edit-heavy (agent-originated decisions dominate)

### Negative Result Criteria (valid failures)
- [ ] **SC-N1:** No tension detected after all completed rounds → "Tasks insufficient to trigger differentiation"
- [ ] **SC-N2:** Tension detected but agents never propose split → "Consolidation loop prefers generic rules at this complexity"
- [ ] **SC-N3:** Splits occur but split arm does not outperform control arm → "Specialization overhead exceeds benefit; continued generic evolution is sufficient"
- [ ] **SC-N4:** Specialists don't generalize to holdout → "Specialist rules overfit to evolution task domains"
- [ ] **SC-N5:** Control arm outperforms split arm → "Structural complexity hurts; simpler is better"

---

## Experiment 2 Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Tasks don't create enough tension | High | Medium | Expanded pilot (4 tasks, all axes) before committing. Executor variance measurement on 2 tasks. If pilot variance < 2.0, redesign tasks |
| Agents never propose a split | Medium | Medium | Tension data explicitly shown to synthesizer; escalation prompt if tension persists 3+ rounds without structural proposal. This is also a valid negative result (SC-N2) |
| Agents propose too many splits too fast | Medium | Low | Human approval gate on every split; every specialist must prove +0.3 within 2 rounds (min 3 routed tasks) or face re-merge; budget burn rate is the natural brake |
| Router misclassifies tasks | Medium | Low | Human review for first 2 rounds post-split; 0.6 confidence threshold with generic fallback; router evaluated separately from specialists (gold labels + downstream score utility) |
| Specialist rules diverge beyond shared base | Medium | Low | Shared base immutable except by consensus across all specialist loops; architecture/integration sub-dimension guardrail (no > 1.0 regression) |
| Budget overrun from two-arm design | High | Medium | $450 ceiling with early termination on convergence (saves $60-120); reduce judge to 2x after R2; control arm can use Sonnet for execution; budget checkpoints at R3, R5 |
| Baseline scores near ceiling (tasks too easy) | Medium | Low | Pilot validates difficulty (target 5.0-9.0 baseline); tasks designed at 300-600 lines with multi-file multi-concern structure |
| Re-merge destroys good specialist rules | Low | Medium | Minimum sample size (3 tasks) + counterfactual comparison before re-merge eligible; human-approved; synthesizer proposes which rules to absorb |
| Control arm invalidates specialization claim | Medium | Medium | This is the whole point — if control arm wins, that's a valid finding (SC-N5). The two-arm design makes the result honest either way |
| Human intervention dominates agent decisions | Medium | Medium | Intervention protocol logs every approval type; if >30% edit-heavy, the "agent-driven" claim is weakened and must be reported (SC-O10) |
| Executor variance exceeds effect size | Medium | Low | Pilot measures executor variance on 2 tasks; if variance > 1.0, raise the +0.3 improvement threshold; post-split counterfactual replays provide direct within-round comparisons |

---

## Experiment 2 Dependency Graph

```
Phase 0 (Setup)
  ├── 0.0a-0.0e: Preflight checklist (gate: all pass before proceeding)
  │
  ├── 0.1-0.2: Structure + seed rules ─────────────────────────┐
  ├── 0.3-0.5: Task specs (14 tasks) ─────────────────────────┤
  ├── 0.6: Tiered test suite (acceptance + property + stress) ─┤
  ├── 0.7-0.8: Judge rubric + sub-dimensions ─────────────────┤ (parallel)
  ├── 0.14-0.19: Scripts (detect_tension, route, split, merge) ┤
  ├── 0.20-0.21: Agent prompts + approval rubric ─────────────┘
  │                                                    │
  ├── 0.9-0.11: Pilot validation (4 tasks + executor variance) ← all above
  ├── 0.12: Freeze tension thresholds ← pilot data
  ├── 0.13: Validate difficulty ← pilot scores
  │         (gate: if baseline > 9.0 or < 5.0, redesign)
  │         (gate: if tension variance < 2.0, redesign)
  │
  ├── 0.22: Update CLAUDE.md
  └── 0.23: /steadows-verify gate
        │
Phase 1 (Baseline — shared between arms) ← Phase 0
  ├── 1.1-1.4: Execute + judge + tension profile (10 tasks) ──┐ (parallel)
  ├── 1.5-1.6: Holdout pre-eval (sealed, isolated worktree) ──┘
  └── 1.7-1.9: Compile + checkpoint + verify gate
        │
Phase 2 (Evolution — 5 rounds × 2 arms) ← Phase 1
  │
  │  ┌────────────────────────────────────────────────────────┐
  │  │  Per round, per arm:                                   │
  │  │    Execute 10 tasks → Test + Judge → Detect tension    │
  │  │    → Consolidate (adaptive or generic-only)            │
  │  │    → Agent proposes: edit/split/merge/none              │
  │  │    → Human approval (logged with intervention type)     │
  │  │    → Apply rules → Post-split counterfactual (if split) │
  │  │    → Checkpoint + budget check                         │
  │  │                                                        │
  │  │  SPLIT ARM: Full structural freedom                    │
  │  │  CONTROL ARM: Rule edits only, no splits               │
  │  │                                                        │
  │  │  Early exit per arm: 2 consecutive "no change"         │
  │  │  Budget checkpoints: R3, R5                            │
  │  └────────────────────────────────────────────────────────┘
  │
  └── 2.14: /steadows-verify gate (both arms)
        │
Phase 3 (Holdout — both arms) ← Phase 2
  ├── 3.1-3.3: Split arm holdout post (routed if specialists) ─┐ (parallel)
  ├── 3.4-3.5: Control arm holdout post (generic rules) ───────┘
  ├── 3.6: Judge all holdout outputs (both arms)
  ├── 3.7: Unseal holdout pre-scores for comparison
  └── 3.8-3.9: Compile + verify gate
        │
Phase 4 (Analysis) ← Phase 3
  ├── 4.1: Split arm vs control arm comparison (PRIMARY RESULT)
  ├── 4.2-4.3: Score trajectories + differentiation analysis ──┐
  ├── 4.4: Counterfactual replay analysis ─────────────────────┤
  ├── 4.5: Tension resolution analysis ────────────────────────┤ (parallel)
  ├── 4.6: Router accuracy analysis ───────────────────────────┤
  ├── 4.7: Negative-control analysis ──────────────────────────┤
  ├── 4.8-4.9: Specialist convergence + holdout generalization ┤
  ├── 4.10: Human intervention analysis ───────────────────────┤
  ├── 4.11-4.14: Cross-experiment + cost + drift + convergence ┘
  │                                                    │
  ├── 4.15: Final report (joins all analyses) ← all above
  ├── 4.16: Dev journal
  ├── 4.17: Git checkpoint
  └── 4.18: /steadows-verify gate (final)
```

---

## References

1. @agentic.james, "AI Agents Self-Organizing Like Biological Cells," Instagram, 2026-03-19
2. Ma, X. et al., "Agentic Neural Networks," arXiv:2506.09046, Jun 2025
3. Tang, J. et al., "HiVA," arXiv:2509.00189, AAAI 2026
4. Razzhigaev, A., "Ouroboros," GitHub, Feb 2026
5. OpenAI, "Self-Evolving Agents Cookbook," Nov 2025
6. Microsoft, "PromptWizard," GitHub
7. Chen, J. et al., "S-Agents: Self-organizing Agents in Open-ended Environments," arXiv:2402.04578, Feb 2024
8. Yang, Y. et al., "AgentNet: Decentralized Evolutionary Coordination," NeurIPS 2025
9. `~/research-workbench/instagram-ai-agents-self-organizing-like-biological-cells/research.html`
