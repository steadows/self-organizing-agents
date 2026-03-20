# GSD Plan: Self-Organizing Agent Experiment in Claude Code

**Created:** 2026-03-19
**Status:** In Progress — Phase 0 ✓, Phase 1 ✓, Phase 2 next
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
**Estimated effort:** 3-4 hours
**Dependency:** Phase 1 + Phase 2 complete

**Why batch consolidation:** Consolidating after a single task gives the critic one data point — not enough to distinguish a rule gap from a task-specific quirk. Batch consolidation gives 5 diverse outputs per round, producing higher-quality rule updates with less noise.

**Session logging:** Every task run must log session metadata to `session-logs/` (model version, session ID, timestamp, token counts).

### Round 1: Execute all 5 tasks with rules v0

Tasks within a round are independent — run concurrently in separate sessions.

- [ ] **3.1** Run task-001 with current rules (v0) → `outputs/evolved/round-01/task-001/`
- [ ] **3.2** Run task-002 with current rules (v0) → `outputs/evolved/round-01/task-002/`
- [ ] **3.3** Run task-003 with current rules (v0) → `outputs/evolved/round-01/task-003/`
- [ ] **3.4** Run task-004 with current rules (v0) → `outputs/evolved/round-01/task-004/`
- [ ] **3.5** Run task-005 with current rules (v0) → `outputs/evolved/round-01/task-005/`
- [ ] **3.6** Run acceptance tests against all 5 outputs
- [ ] **3.7** Judge all 5 outputs (run 3x each, take median). Cross-check against acceptance test results
- [ ] **3.8** Consolidation round 1: critic/defender/synthesizer review ALL 5 outputs + scores + acceptance test results → proposal to `consolidation/proposals/round-01.md` → human reviews against `approval-rubric.md` → decision + rationale recorded in `consolidation/approvals/round-01.md` → if approved, apply via `apply_rules.py` → creates `rules/v1/`
- [ ] **3.9** Git checkpoint: `data: evolved round 1 scores + rules v1`

### Round 2: Execute all 5 tasks with rules v1

- [ ] **3.10** Run task-001 with evolved rules (v1) → `outputs/evolved/round-02/task-001/`
- [ ] **3.11** Run task-002 with evolved rules (v1) → `outputs/evolved/round-02/task-002/`
- [ ] **3.12** Run task-003 with evolved rules (v1) → `outputs/evolved/round-02/task-003/`
- [ ] **3.13** Run task-004 with evolved rules (v1) → `outputs/evolved/round-02/task-004/`
- [ ] **3.14** Run task-005 with evolved rules (v1) → `outputs/evolved/round-02/task-005/`
- [ ] **3.15** Run acceptance tests against all 5 outputs
- [ ] **3.16** Judge all 5 outputs. Cross-check against acceptance test results
- [ ] **3.17** Consolidation round 2: review ALL 5 outputs + scores + diff from round 1 → human approval (same protocol) → apply → creates `rules/v2/`
- [ ] **3.18** Git checkpoint: `data: evolved round 2 scores + rules v2`

### Round 3: Execute all 5 tasks with rules v2 (final measurement)

- [ ] **3.19** Run task-001 with evolved rules (v2) → `outputs/evolved/round-03/task-001/`
- [ ] **3.20** Run task-002 with evolved rules (v2) → `outputs/evolved/round-03/task-002/`
- [ ] **3.21** Run task-003 with evolved rules (v2) → `outputs/evolved/round-03/task-003/`
- [ ] **3.22** Run task-004 with evolved rules (v2) → `outputs/evolved/round-03/task-004/`
- [ ] **3.23** Run task-005 with evolved rules (v2) → `outputs/evolved/round-03/task-005/`
- [ ] **3.24** Run acceptance tests against all 5 outputs
- [ ] **3.25** Judge all 5 outputs (no consolidation — this is the final measurement)

### Holdout Post-Evaluation (generalization test — isolated worktree)

Run in a **fresh git worktree** containing only `rules/v2/` + `holdout/` directory (specs + acceptance tests + pre outputs). No evolution outputs, no evolution task history visible. Same artifact flow as Phase 1 holdout.

- [ ] **3.26** Create isolated worktree for holdout post-evaluation (rules v2 + `holdout/` directory)
- [ ] **3.27** Run holdout-001 in worktree with evolved rules (v2) → `holdout/outputs/post/holdout-001/`
- [ ] **3.28** Run holdout-002 in worktree → `holdout/outputs/post/holdout-002/`
- [ ] **3.29** Run holdout-003 in worktree → `holdout/outputs/post/holdout-003/`
- [ ] **3.30** Run holdout acceptance tests in worktree against all 3 outputs. Record pass/fail per test case
- [ ] **3.31** Judge all 3 holdout outputs in worktree (same 3x median protocol)
- [ ] **3.32** Commit holdout post outputs + scores inside worktree. Merge worktree branch to main. Delete worktree. Post outputs now exist in `holdout/outputs/post/` in the repo

### Compile and Checkpoint

- [ ] **3.33** Compile all evolved scores → `scores/evolved-scores.json` (per-round, per-task, per-dimension)
- [ ] **3.34** Compile holdout scores → `scores/holdout-scores.json` (pre vs post, per-task, per-dimension, including acceptance test pass rates)
- [ ] **3.35** Git checkpoint: `data: evolved round 3 + holdout post scores (final)`
- [ ] **3.36** **`/steadows-verify`** — Phase 3 quality gate. Verify: all 15 evolved outputs exist in `outputs/evolved/` (5 tasks x 3 rounds), all 3 holdout pre outputs exist in `holdout/outputs/pre/`, all 3 holdout post outputs exist in `holdout/outputs/post/`, all acceptance tests ran per round with recorded results, all judge scores recorded with 3x medians, correctness scores consistent with acceptance results, 2 consolidation proposals generated with approval rationales recorded in `consolidation/approvals/`, rules versions v1-v2 exist with valid diffs and attribution labels, each rule file under 150 lines, `rules/current` symlink points to v2, all session logs captured (all invocation types: executor + judge + consolidation agents), no files modified outside sandbox

---

## Phase 4: Measurement & Analysis

**Goal:** Compare baseline vs evolved. Analyze rule drift. Report findings.
**Estimated effort:** 1-2 hours
**Dependency:** Phase 1 + Phase 3 complete

- [ ] **4.1** Score comparison (`analysis/comparison.md`) — baseline vs round 1 vs round 2 vs round 3, per-dimension and overall deltas, per-task trends across rounds. Include both LLM judge scores and acceptance test pass rates
- [ ] **4.2** Holdout generalization analysis (`analysis/holdout-analysis.md`) — compare holdout pre (rules v0) vs holdout post (rules v2). **This is the key generalization test.** If holdout scores improve, the rules generalized beyond the 5 evolution tasks. If only evolution-set scores improve, the rules overfit. Report the delta with the same rigor as the main comparison
- [ ] **4.3** Behavioral drift analysis (`analysis/drift-analysis.md`) — diff rules v0→v1→v2, categorize changes (new guidance, clarification, removal, restructuring), flag bloat, measure rule file growth in lines, verify all changes have attribution labels
- [ ] **4.4** Cost tracking (`analysis/cost-tracking.md`) — tokens per round from `session-logs/`, broken down by invocation type (executor, judge, consolidation). Cost per quality-point improvement. Baseline phase vs evolved phase total. Total experiment cost vs $85 budget ceiling
- [ ] **4.5** Convergence analysis (`analysis/convergence.md`) — do per-round averages improve monotonically? does round 3 plateau vs round 2? which dimensions converge fastest? do any tasks resist improvement across all rounds? do acceptance test pass rates correlate with judge scores?
- [ ] **4.6** Experiment report (`analysis/report.md`) — hypothesis, methodology, results (including holdout), findings, limitations (including: human approval as confound, task complexity ceiling, model-specific results), recommendations for whether to proceed to Experiment 2
- [ ] **4.7** Dev journal entry (`~/dev-journal/2026-03-XX.md`)
- [ ] **4.8** Final git commit: `docs: experiment analysis and report`
- [ ] **4.9** **`/steadows-verify`** — Phase 4 quality gate (final). Verify: all analysis files exist, comparison includes per-dimension deltas, holdout analysis explicitly states generalization verdict, drift analysis covers all rule versions with attribution labels, cost tracking sourced from session-logs with per-round breakdown, convergence analysis addresses plateau question, report includes methodology + results + holdout + limitations, all success criteria evaluated, experiment is fully reproducible from git history

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
| 3.36 | Evolved | `/steadows-verify` | All 15 evolved + 6 isolated holdout outputs, acceptance tests, scores, rule versions, approval records with rationale, session logs (all invocation types), sandbox |
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
