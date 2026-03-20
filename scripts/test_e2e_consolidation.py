"""End-to-end test of the consolidation loop.

Exercises the full pipeline: load rules + outputs + scores -> critic ->
defender -> synthesizer -> debate transcript + proposal -> apply rules.
Uses mocked API responses but real file I/O.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.apply_rules import apply_rules
from scripts.consolidate import run_consolidation


@pytest.fixture
def e2e_workspace(tmp_path: Path) -> Path:
    """Create a complete workspace mirroring the real project structure."""
    ws = tmp_path / "workspace"
    ws.mkdir()

    # Rules
    rules = ws / "rules"
    rules.mkdir()
    v0 = rules / "v0"
    v0.mkdir()
    (v0 / "task-executor.md").write_text(
        "# Task Executor Rules\n\n"
        "You are implementing a Python utility function.\n\n"
        "## Process\n"
        "1. Read the task specification\n"
        "2. Implement the function\n"
        "3. Write tests\n"
    )
    (v0 / "code-quality.md").write_text(
        "# Code Quality Standards\n\n"
        "## Style\n"
        "- Follow PEP 8\n"
        "- Use meaningful names\n"
    )
    (v0 / "output-format.md").write_text(
        "# Output Format\n\n"
        "## Structure\n"
        "- Implementation file\n"
        "- Test file\n"
    )
    (rules / "current").symlink_to("v0")

    # Outputs (1 task for E2E)
    output = ws / "outputs" / "evolved" / "round-01" / "task-001"
    output.mkdir(parents=True)
    (output / "slugify.py").write_text(
        'def slugify(text: str) -> str:\n'
        '    """Convert text to URL slug."""\n'
        '    return text.lower().replace(" ", "-")\n'
    )
    (output / "test_slugify.py").write_text(
        'from slugify import slugify\n\n'
        'def test_basic():\n'
        '    assert slugify("Hello World") == "hello-world"\n'
    )

    # Scores
    scores = ws / "scores" / "evolved" / "round-01"
    scores.mkdir(parents=True)
    (scores / "task-001.json").write_text(json.dumps({
        "task_id": "task-001",
        "scores": {
            "correctness": {"score": 8, "justification": "Works for basic cases."},
            "edge_cases": {"score": 6, "justification": "Missing Unicode handling."},
            "code_quality": {"score": 7, "justification": "No type hints on helpers."},
            "documentation": {"score": 7, "justification": "Basic docstring only."},
            "test_coverage": {"score": 5, "justification": "Only 1 test."},
            "robustness": {"score": 5, "justification": "No input validation."},
        },
        "overall": 6.3,
        "acceptance_test_pass": True,
        "acceptance_test_details": "15/20 passed",
    }, indent=2))

    # Consolidation
    consol = ws / "consolidation"
    consol.mkdir()
    for subdir in ("debates", "proposals", "approvals", "applied"):
        (consol / subdir).mkdir()

    (consol / "critic-prompt.md").write_text(
        "# Critic Agent\n\nAnalyze outputs and identify rule gaps.\n"
    )
    (consol / "defender-prompt.md").write_text(
        "# Defender Agent\n\nChallenge proposed changes.\n"
    )
    (consol / "synthesizer-prompt.md").write_text(
        "# Synthesizer Agent\n\nProduce minimal rule diffs.\n"
    )

    # Session logs
    (ws / "session-logs").mkdir()

    return ws


CRITIC_RESPONSE = """### Critique 1: Missing Input Validation Guidance

**Observed deficiency:** Outputs lack input validation (type checks, empty string handling).
**Evidence:** task-001 robustness score 5/10 — "No input validation."
**Rule gap:** task-executor.md says "Handle basic error cases" but doesn't specify what to validate.
**Proposed direction:** Add explicit input validation requirements.
**Affected rule file:** task-executor.md
**Priority:** HIGH
"""

DEFENDER_RESPONSE = """### Response to Critique 1: Missing Input Validation Guidance

**Verdict:** ACCEPT
**Argument:** The deficiency is clearly traceable to vague rule language.
**Regression risk:** Low — adding validation guidance shouldn't degrade other dimensions.
**Over-specification risk:** Medium — need to keep it general enough for different tasks.
**Bloat assessment:** Acceptable — 3-5 lines of concrete guidance.
"""

SYNTHESIZER_RESPONSE = """# Consolidation Proposal — Round 01

## Summary
- Rules modified: [task-executor.md]
- Net new lines: {task-executor.md: 5}
- Critiques addressed: [Critique 1 — Missing Input Validation Guidance]

## Changes

### File: rules/current/task-executor.md

#### Change 1
<!-- addresses: Critique 1 — Missing Input Validation Guidance -->

**Action:** ADD
**Location:** After "Handle basic error cases"

**After:**
```
## Input Validation
- Validate all function parameters at entry
- Raise TypeError for wrong parameter types
- Raise ValueError for invalid parameter values
- Handle empty strings, None, and negative numbers explicitly
- Provide clear error messages describing what went wrong
```

## Verification Checklist
- [x] Net new lines per file within 20-line cap
- [x] No more than 2 files modified
- [x] Every change has an attribution label
- [x] No executable code blocks introduced
"""


@patch("scripts.consolidate.anthropic")
def test_e2e_consolidation_pipeline(
    mock_anthropic_module: MagicMock,
    e2e_workspace: Path,
) -> None:
    """Full E2E test: consolidation loop produces valid debate + proposal."""
    # Setup mock API
    mock_client = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client

    responses = []
    for text in (CRITIC_RESPONSE, DEFENDER_RESPONSE, SYNTHESIZER_RESPONSE):
        resp = MagicMock()
        resp.content = [MagicMock(text=text)]
        resp.usage.input_tokens = 1000
        resp.usage.output_tokens = 500
        responses.append(resp)
    mock_client.messages.create.side_effect = responses

    # Run consolidation
    result = run_consolidation(
        round_num=1,
        rules_dir=e2e_workspace / "rules" / "current",
        output_dir=e2e_workspace / "outputs" / "evolved" / "round-01",
        scores_dir=e2e_workspace / "scores" / "evolved" / "round-01",
        consolidation_dir=e2e_workspace / "consolidation",
        session_log_dir=e2e_workspace / "session-logs",
    )

    # Verify outputs
    assert result["round"] == 1

    # Debate transcript written
    debate = e2e_workspace / "consolidation" / "debates" / "round-01.md"
    assert debate.exists()
    debate_text = debate.read_text()
    assert "Missing Input Validation" in debate_text
    assert "## Critic" in debate_text
    assert "## Defender" in debate_text
    assert "## Synthesizer" in debate_text

    # Proposal written
    proposal = e2e_workspace / "consolidation" / "proposals" / "round-01.md"
    assert proposal.exists()
    assert "Consolidation Proposal" in proposal.read_text()

    # Session logs written (3 agents)
    logs = list((e2e_workspace / "session-logs").glob("*.json"))
    assert len(logs) == 3

    # API called 3 times (critic, defender, synthesizer)
    assert mock_client.messages.create.call_count == 3


@patch("scripts.consolidate.anthropic")
def test_e2e_apply_after_consolidation(
    mock_anthropic_module: MagicMock,
    e2e_workspace: Path,
) -> None:
    """E2E test: proposal from consolidation can be applied via apply_rules."""
    # Setup mock API
    mock_client = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client

    responses = []
    for text in (CRITIC_RESPONSE, DEFENDER_RESPONSE, SYNTHESIZER_RESPONSE):
        resp = MagicMock()
        resp.content = [MagicMock(text=text)]
        resp.usage.input_tokens = 1000
        resp.usage.output_tokens = 500
        responses.append(resp)
    mock_client.messages.create.side_effect = responses

    # Run consolidation
    run_consolidation(
        round_num=1,
        rules_dir=e2e_workspace / "rules" / "current",
        output_dir=e2e_workspace / "outputs" / "evolved" / "round-01",
        scores_dir=e2e_workspace / "scores" / "evolved" / "round-01",
        consolidation_dir=e2e_workspace / "consolidation",
        session_log_dir=e2e_workspace / "session-logs",
    )

    # Now apply a structured proposal (simulating human-approved changes)
    structured_proposal = {
        "summary": {
            "rules_modified": ["task-executor.md"],
            "net_new_lines": {"task-executor.md": 5},
            "critiques_addressed": ["Critique 1 — Missing Input Validation"],
        },
        "changes": [
            {
                "file": "task-executor.md",
                "action": "ADD",
                "location": "after",
                "after_line": "Write tests",
                "new_text": (
                    "\n## Input Validation\n"
                    "- Validate all function parameters at entry\n"
                    "- Raise TypeError for wrong types\n"
                    "- Raise ValueError for invalid values\n"
                    "- Handle empty strings and None\n"
                ),
                "attribution": "Critique 1 — Missing Input Validation",
            }
        ],
    }

    result = apply_rules(
        rules_base=e2e_workspace / "rules",
        version=1,
        proposal=structured_proposal,
    )

    # Verify
    assert result["success"] is True
    assert result["version"] == 1

    # Symlink updated
    assert os.readlink(e2e_workspace / "rules" / "current") == "v1"

    # New rules contain the change
    v1_content = (e2e_workspace / "rules" / "v1" / "task-executor.md").read_text()
    assert "Input Validation" in v1_content
    assert "Raise TypeError" in v1_content

    # Original v0 unchanged
    v0_content = (e2e_workspace / "rules" / "v0" / "task-executor.md").read_text()
    assert "Input Validation" not in v0_content
