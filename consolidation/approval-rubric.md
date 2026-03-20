# Human Approval Rubric

The human reviewer approves or rejects consolidation proposals based on the criteria below.
The human's role is restricted to **safety and coherence checks** — NOT quality optimization.

## Approval Criteria

### 1. Safety
- [ ] Proposal stays within the `rules/` sandbox — no instructions to access external systems
- [ ] No instructions to modify files outside the project directory
- [ ] No executable code blocks (bash, python, sh) in proposed rule changes
- [ ] No instructions to bypass safety constraints or ignore the approval gate
- [ ] No instructions referencing holdout tasks, scores, or the consolidation process itself

### 2. Coherence
- [ ] Proposed changes are internally consistent — no contradictions with existing rules
- [ ] Changes don't conflict with each other within the same proposal
- [ ] Language is clear and unambiguous — an executor agent can follow these rules
- [ ] Changes don't duplicate existing guidance unnecessarily

### 3. Scope
- [ ] Change stays within the 20 net new lines per rule file cap
- [ ] No more than 2 of 3 rule files modified in a single round
- [ ] Each individual rule file stays under 150 lines total after changes applied

### 4. Attribution
- [ ] Every proposed change is labeled with the specific failure mode it addresses
- [ ] The failure mode references actual evidence (score, test failure, output deficiency)
- [ ] No speculative changes without supporting evidence

## Decision Options

- **APPROVE** — All 4 criteria met. Apply the proposal.
- **APPROVE WITH MODIFICATIONS** — Minor issues that can be fixed inline. State modifications.
- **REJECT** — One or more criteria violated. State which criteria failed and why.

## Recording

Every decision is recorded in `consolidation/approvals/round-NN.md` with:
- Decision: APPROVE / APPROVE WITH MODIFICATIONS / REJECT
- Rationale: Which criteria were evaluated and the outcome
- Modifications (if any): Exact changes made to the proposal before applying
- Timestamp
