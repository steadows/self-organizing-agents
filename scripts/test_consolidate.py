"""Tests for consolidation loop orchestrator.

Tests prompt assembly, agent invocation sequence, proposal output format,
and debate transcript capture. Written BEFORE implementation (TDD).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

from scripts.consolidate import (
    build_critic_prompt,
    build_defender_prompt,
    build_synthesizer_prompt,
    load_outputs,
    load_rules,
    load_scores,
    log_session,
    run_agent,
    run_consolidation,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_RULE_CONTENT = "# Task Executor Rules\n\nDo the thing.\n"
SAMPLE_OUTPUT_CODE = 'def slugify(text: str) -> str:\n    return text.lower()\n'
SAMPLE_TEST_CODE = 'def test_slugify():\n    assert slugify("Hi") == "hi"\n'


@pytest.fixture
def rules_dir(tmp_path: Path) -> Path:
    """Create a minimal rules directory with 3 rule files."""
    d = tmp_path / "rules" / "v0"
    d.mkdir(parents=True)
    (d / "task-executor.md").write_text("# Task Executor\n\nFollow instructions.\n")
    (d / "code-quality.md").write_text("# Code Quality\n\nWrite clean code.\n")
    (d / "output-format.md").write_text("# Output Format\n\nUse proper structure.\n")
    return d


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create output directories for 2 tasks with implementation + test files."""
    base = tmp_path / "outputs" / "evolved" / "round-01"
    for task_id in ("task-001", "task-002"):
        task_dir = base / task_id
        task_dir.mkdir(parents=True)
        (task_dir / "slugify.py").write_text(SAMPLE_OUTPUT_CODE)
        (task_dir / "test_slugify.py").write_text(SAMPLE_TEST_CODE)
    return base


@pytest.fixture
def scores_dir(tmp_path: Path) -> Path:
    """Create score JSON files for 2 tasks."""
    d = tmp_path / "scores" / "evolved" / "round-01"
    d.mkdir(parents=True)
    for task_id in ("task-001", "task-002"):
        score = _make_score(task_id)
        (d / f"{task_id}.json").write_text(json.dumps(score, indent=2))
    return d


@pytest.fixture
def consolidation_dir(tmp_path: Path) -> Path:
    """Create the consolidation directory with agent prompts."""
    d = tmp_path / "consolidation"
    d.mkdir(parents=True)
    for subdir in ("debates", "proposals", "approvals", "applied"):
        (d / subdir).mkdir()
    (d / "critic-prompt.md").write_text("# Critic Agent\n\nFind rule gaps.\n")
    (d / "defender-prompt.md").write_text("# Defender Agent\n\nPush back.\n")
    (d / "synthesizer-prompt.md").write_text("# Synthesizer Agent\n\nResolve debates.\n")
    return d


@pytest.fixture
def session_log_dir(tmp_path: Path) -> Path:
    """Create session log directory."""
    d = tmp_path / "session-logs"
    d.mkdir()
    return d


def _make_score(task_id: str, overall: float = 7.5) -> dict[str, Any]:
    """Create a sample score dictionary."""
    return {
        "task_id": task_id,
        "phase": "evolved",
        "rules_version": "v0",
        "scores": {
            "correctness": {"score": 8, "justification": "Good."},
            "edge_cases": {"score": 7, "justification": "Decent."},
            "code_quality": {"score": 8, "justification": "Clean."},
            "documentation": {"score": 7, "justification": "Adequate."},
            "test_coverage": {"score": 8, "justification": "Thorough."},
            "robustness": {"score": 6, "justification": "Missing input validation."},
        },
        "overall": overall,
        "acceptance_test_pass": True,
        "acceptance_test_details": "15/15 passed",
    }


# ---------------------------------------------------------------------------
# TestLoadRules
# ---------------------------------------------------------------------------


class TestLoadRules:
    """Tests for load_rules()."""

    def test_loads_all_markdown_files(self, rules_dir: Path) -> None:
        """Should return a dict of filename -> content for all .md files."""
        rules = load_rules(rules_dir)
        assert set(rules.keys()) == {
            "task-executor.md",
            "code-quality.md",
            "output-format.md",
        }

    def test_content_matches_files(self, rules_dir: Path) -> None:
        """Each value should be the full file content."""
        rules = load_rules(rules_dir)
        assert "Follow instructions." in rules["task-executor.md"]

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError for non-existent directory."""
        with pytest.raises(FileNotFoundError):
            load_rules(tmp_path / "nonexistent")

    def test_ignores_non_markdown_files(self, rules_dir: Path) -> None:
        """Should skip files that aren't .md."""
        (rules_dir / "notes.txt").write_text("ignore me")
        rules = load_rules(rules_dir)
        assert "notes.txt" not in rules


# ---------------------------------------------------------------------------
# TestLoadOutputs
# ---------------------------------------------------------------------------


class TestLoadOutputs:
    """Tests for load_outputs()."""

    def test_loads_all_task_directories(self, output_dir: Path) -> None:
        """Should return a dict keyed by task directory name."""
        outputs = load_outputs(output_dir)
        assert set(outputs.keys()) == {"task-001", "task-002"}

    def test_concatenates_python_files(self, output_dir: Path) -> None:
        """Each task value should contain all .py file contents."""
        outputs = load_outputs(output_dir)
        assert "def slugify" in outputs["task-001"]
        assert "def test_slugify" in outputs["task-001"]

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError for non-existent directory."""
        with pytest.raises(FileNotFoundError):
            load_outputs(tmp_path / "nonexistent")

    def test_skips_non_directory_entries(self, output_dir: Path) -> None:
        """Should ignore files at the top level of the output dir."""
        (output_dir / "README.md").write_text("ignore me")
        outputs = load_outputs(output_dir)
        assert "README.md" not in outputs


# ---------------------------------------------------------------------------
# TestLoadScores
# ---------------------------------------------------------------------------


class TestLoadScores:
    """Tests for load_scores()."""

    def test_loads_all_score_files(self, scores_dir: Path) -> None:
        """Should return a dict keyed by task_id from filename."""
        scores = load_scores(scores_dir)
        assert set(scores.keys()) == {"task-001", "task-002"}

    def test_score_structure(self, scores_dir: Path) -> None:
        """Each score should have the expected keys."""
        scores = load_scores(scores_dir)
        assert "overall" in scores["task-001"]
        assert "scores" in scores["task-001"]

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError for non-existent directory."""
        with pytest.raises(FileNotFoundError):
            load_scores(tmp_path / "nonexistent")


# ---------------------------------------------------------------------------
# TestBuildCriticPrompt
# ---------------------------------------------------------------------------


class TestBuildCriticPrompt:
    """Tests for build_critic_prompt()."""

    def test_includes_system_prompt(self, consolidation_dir: Path) -> None:
        """Should include the critic agent prompt template."""
        prompt = build_critic_prompt(
            prompt_path=consolidation_dir / "critic-prompt.md",
            rules={"task-executor.md": "# Rules\nDo things."},
            outputs={"task-001": "def foo(): pass"},
            scores={"task-001": _make_score("task-001")},
        )
        assert "Find rule gaps" in prompt

    def test_includes_all_rules(self, consolidation_dir: Path) -> None:
        """Prompt should contain all rule file contents."""
        rules = {
            "task-executor.md": "RULE_A_CONTENT",
            "code-quality.md": "RULE_B_CONTENT",
        }
        prompt = build_critic_prompt(
            prompt_path=consolidation_dir / "critic-prompt.md",
            rules=rules,
            outputs={"task-001": "code"},
            scores={"task-001": _make_score("task-001")},
        )
        assert "RULE_A_CONTENT" in prompt
        assert "RULE_B_CONTENT" in prompt

    def test_includes_all_outputs(self, consolidation_dir: Path) -> None:
        """Prompt should contain code from all task outputs."""
        outputs = {"task-001": "CODE_FOR_001", "task-002": "CODE_FOR_002"}
        prompt = build_critic_prompt(
            prompt_path=consolidation_dir / "critic-prompt.md",
            rules={"r.md": "rule"},
            outputs=outputs,
            scores={
                "task-001": _make_score("task-001"),
                "task-002": _make_score("task-002"),
            },
        )
        assert "CODE_FOR_001" in prompt
        assert "CODE_FOR_002" in prompt

    def test_includes_scores_as_json(self, consolidation_dir: Path) -> None:
        """Prompt should contain score data in a parseable format."""
        scores = {"task-001": _make_score("task-001")}
        prompt = build_critic_prompt(
            prompt_path=consolidation_dir / "critic-prompt.md",
            rules={"r.md": "rule"},
            outputs={"task-001": "code"},
            scores=scores,
        )
        # Score justification text should appear in the prompt
        assert "Missing input validation" in prompt


# ---------------------------------------------------------------------------
# TestBuildDefenderPrompt
# ---------------------------------------------------------------------------


class TestBuildDefenderPrompt:
    """Tests for build_defender_prompt()."""

    def test_includes_critic_response(self, consolidation_dir: Path) -> None:
        """Prompt should include the critic's output."""
        prompt = build_defender_prompt(
            prompt_path=consolidation_dir / "defender-prompt.md",
            rules={"r.md": "rule"},
            critic_response="CRITIC_SAID_THIS",
            scores={"task-001": _make_score("task-001")},
        )
        assert "CRITIC_SAID_THIS" in prompt

    def test_includes_rules(self, consolidation_dir: Path) -> None:
        """Prompt should include current rules for context."""
        prompt = build_defender_prompt(
            prompt_path=consolidation_dir / "defender-prompt.md",
            rules={"task-executor.md": "RULE_CONTENT"},
            critic_response="critique",
            scores={"task-001": _make_score("task-001")},
        )
        assert "RULE_CONTENT" in prompt


# ---------------------------------------------------------------------------
# TestBuildSynthesizerPrompt
# ---------------------------------------------------------------------------


class TestBuildSynthesizerPrompt:
    """Tests for build_synthesizer_prompt()."""

    def test_includes_critic_and_defender(self, consolidation_dir: Path) -> None:
        """Prompt should include both critic and defender responses."""
        prompt = build_synthesizer_prompt(
            prompt_path=consolidation_dir / "synthesizer-prompt.md",
            rules={"r.md": "rule"},
            critic_response="CRITIC_OUTPUT",
            defender_response="DEFENDER_OUTPUT",
            scores={"task-001": _make_score("task-001")},
        )
        assert "CRITIC_OUTPUT" in prompt
        assert "DEFENDER_OUTPUT" in prompt

    def test_includes_rules(self, consolidation_dir: Path) -> None:
        """Prompt should include current rules for the synthesizer to edit."""
        prompt = build_synthesizer_prompt(
            prompt_path=consolidation_dir / "synthesizer-prompt.md",
            rules={"task-executor.md": "SYNTH_RULE"},
            critic_response="c",
            defender_response="d",
            scores={"task-001": _make_score("task-001")},
        )
        assert "SYNTH_RULE" in prompt


# ---------------------------------------------------------------------------
# TestRunAgent
# ---------------------------------------------------------------------------


class TestRunAgent:
    """Tests for run_agent()."""

    def test_calls_api_with_correct_params(self) -> None:
        """Should call anthropic messages.create with expected arguments."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="agent response")]
        mock_response.usage.input_tokens = 500
        mock_response.usage.output_tokens = 200
        mock_client.messages.create.return_value = mock_response

        text, usage = run_agent(
            client=mock_client,
            model="claude-sonnet-4-6",
            prompt="Do your job.",
            max_tokens=8192,
        )

        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-6"
        assert call_kwargs["max_tokens"] == 8192

    def test_returns_response_text(self) -> None:
        """Should return the text from the LLM response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="THE RESPONSE")]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        mock_client.messages.create.return_value = mock_response

        text, usage = run_agent(
            client=mock_client,
            model="claude-sonnet-4-6",
            prompt="test",
            max_tokens=4096,
        )

        assert text == "THE RESPONSE"

    def test_returns_usage_metadata(self) -> None:
        """Should return token usage for session logging."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="response")]
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 500
        mock_client.messages.create.return_value = mock_response

        text, usage = run_agent(
            client=mock_client,
            model="claude-sonnet-4-6",
            prompt="test",
            max_tokens=4096,
        )

        assert usage["input_tokens"] == 1000
        assert usage["output_tokens"] == 500


# ---------------------------------------------------------------------------
# TestRunConsolidation
# ---------------------------------------------------------------------------


class TestRunConsolidation:
    """Tests for run_consolidation() — the main orchestrator."""

    @patch("scripts.consolidate.anthropic")
    def test_invokes_three_agents_in_sequence(
        self,
        mock_anthropic_module: MagicMock,
        rules_dir: Path,
        output_dir: Path,
        scores_dir: Path,
        consolidation_dir: Path,
        session_log_dir: Path,
    ) -> None:
        """Should call the API exactly 3 times: critic, defender, synthesizer."""
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client
        self._setup_mock_responses(mock_client)

        run_consolidation(
            round_num=1,
            rules_dir=rules_dir,
            output_dir=output_dir,
            scores_dir=scores_dir,
            consolidation_dir=consolidation_dir,
            session_log_dir=session_log_dir,
        )

        assert mock_client.messages.create.call_count == 3

    @patch("scripts.consolidate.anthropic")
    def test_writes_debate_transcript(
        self,
        mock_anthropic_module: MagicMock,
        rules_dir: Path,
        output_dir: Path,
        scores_dir: Path,
        consolidation_dir: Path,
        session_log_dir: Path,
    ) -> None:
        """Should write full debate to consolidation/debates/round-NN.md."""
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client
        self._setup_mock_responses(mock_client)

        run_consolidation(
            round_num=1,
            rules_dir=rules_dir,
            output_dir=output_dir,
            scores_dir=scores_dir,
            consolidation_dir=consolidation_dir,
            session_log_dir=session_log_dir,
        )

        debate_file = consolidation_dir / "debates" / "round-01.md"
        assert debate_file.exists()
        content = debate_file.read_text()
        assert "CRITIC_RESPONSE" in content
        assert "DEFENDER_RESPONSE" in content
        assert "SYNTHESIZER_RESPONSE" in content

    @patch("scripts.consolidate.anthropic")
    def test_writes_proposal_file(
        self,
        mock_anthropic_module: MagicMock,
        rules_dir: Path,
        output_dir: Path,
        scores_dir: Path,
        consolidation_dir: Path,
        session_log_dir: Path,
    ) -> None:
        """Should write synthesizer output to consolidation/proposals/round-NN.md."""
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client
        self._setup_mock_responses(mock_client)

        run_consolidation(
            round_num=1,
            rules_dir=rules_dir,
            output_dir=output_dir,
            scores_dir=scores_dir,
            consolidation_dir=consolidation_dir,
            session_log_dir=session_log_dir,
        )

        proposal_file = consolidation_dir / "proposals" / "round-01.md"
        assert proposal_file.exists()
        assert "SYNTHESIZER_RESPONSE" in proposal_file.read_text()

    @patch("scripts.consolidate.anthropic")
    def test_returns_result_dict(
        self,
        mock_anthropic_module: MagicMock,
        rules_dir: Path,
        output_dir: Path,
        scores_dir: Path,
        consolidation_dir: Path,
        session_log_dir: Path,
    ) -> None:
        """Should return a dict with round, agents, and file paths."""
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client
        self._setup_mock_responses(mock_client)

        result = run_consolidation(
            round_num=1,
            rules_dir=rules_dir,
            output_dir=output_dir,
            scores_dir=scores_dir,
            consolidation_dir=consolidation_dir,
            session_log_dir=session_log_dir,
        )

        assert result["round"] == 1
        assert "debate_file" in result
        assert "proposal_file" in result
        assert "critic_response" in result
        assert "defender_response" in result
        assert "synthesizer_response" in result

    @patch("scripts.consolidate.anthropic")
    def test_logs_session_metadata(
        self,
        mock_anthropic_module: MagicMock,
        rules_dir: Path,
        output_dir: Path,
        scores_dir: Path,
        consolidation_dir: Path,
        session_log_dir: Path,
    ) -> None:
        """Should write session log entries for each agent invocation."""
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client
        self._setup_mock_responses(mock_client)

        run_consolidation(
            round_num=1,
            rules_dir=rules_dir,
            output_dir=output_dir,
            scores_dir=scores_dir,
            consolidation_dir=consolidation_dir,
            session_log_dir=session_log_dir,
        )

        log_files = list(session_log_dir.glob("consolidation-*.json"))
        assert len(log_files) == 3  # one per agent

    @patch("scripts.consolidate.anthropic")
    def test_debate_includes_section_headers(
        self,
        mock_anthropic_module: MagicMock,
        rules_dir: Path,
        output_dir: Path,
        scores_dir: Path,
        consolidation_dir: Path,
        session_log_dir: Path,
    ) -> None:
        """Debate transcript should have clear section headers for each agent."""
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client
        self._setup_mock_responses(mock_client)

        run_consolidation(
            round_num=1,
            rules_dir=rules_dir,
            output_dir=output_dir,
            scores_dir=scores_dir,
            consolidation_dir=consolidation_dir,
            session_log_dir=session_log_dir,
        )

        debate_file = consolidation_dir / "debates" / "round-01.md"
        content = debate_file.read_text()
        assert "# Critic" in content or "## Critic" in content
        assert "# Defender" in content or "## Defender" in content
        assert "# Synthesizer" in content or "## Synthesizer" in content

    @patch("scripts.consolidate.anthropic")
    def test_round_number_formatting(
        self,
        mock_anthropic_module: MagicMock,
        rules_dir: Path,
        output_dir: Path,
        scores_dir: Path,
        consolidation_dir: Path,
        session_log_dir: Path,
    ) -> None:
        """Round numbers should be zero-padded to 2 digits in filenames."""
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client
        self._setup_mock_responses(mock_client)

        run_consolidation(
            round_num=2,
            rules_dir=rules_dir,
            output_dir=output_dir,
            scores_dir=scores_dir,
            consolidation_dir=consolidation_dir,
            session_log_dir=session_log_dir,
        )

        assert (consolidation_dir / "debates" / "round-02.md").exists()
        assert (consolidation_dir / "proposals" / "round-02.md").exists()

    def _setup_mock_responses(self, mock_client: MagicMock) -> None:
        """Configure mock client to return 3 sequential responses."""
        responses = []
        for agent_text in (
            "CRITIC_RESPONSE",
            "DEFENDER_RESPONSE",
            "SYNTHESIZER_RESPONSE",
        ):
            resp = MagicMock()
            resp.content = [MagicMock(text=agent_text)]
            resp.usage.input_tokens = 500
            resp.usage.output_tokens = 300
            responses.append(resp)

        mock_client.messages.create.side_effect = responses


# ---------------------------------------------------------------------------
# TestLogSession
# ---------------------------------------------------------------------------


class TestLogSession:
    """Tests for log_session()."""

    def test_creates_log_file(self, session_log_dir: Path) -> None:
        """Should write a JSON file to the session log directory."""
        metadata = {
            "invocation_type": "consolidation-critic",
            "round": 1,
            "model": "claude-sonnet-4-6",
            "input_tokens": 500,
            "output_tokens": 300,
        }
        log_path = log_session(session_log_dir, metadata)
        assert log_path.exists()
        assert log_path.suffix == ".json"

    def test_log_content_matches_metadata(self, session_log_dir: Path) -> None:
        """Log file content should match the provided metadata."""
        metadata = {
            "invocation_type": "consolidation-defender",
            "round": 1,
            "model": "claude-sonnet-4-6",
            "input_tokens": 1000,
            "output_tokens": 500,
        }
        log_path = log_session(session_log_dir, metadata)
        saved = json.loads(log_path.read_text())
        assert saved["invocation_type"] == "consolidation-defender"
        assert saved["input_tokens"] == 1000

    def test_log_filename_includes_type(self, session_log_dir: Path) -> None:
        """Log filename should include the invocation type."""
        metadata = {"invocation_type": "consolidation-synthesizer", "round": 1}
        log_path = log_session(session_log_dir, metadata)
        assert "consolidation-synthesizer" in log_path.name

    def test_creates_directory_if_missing(self, tmp_path: Path) -> None:
        """Should create the log directory if it doesn't exist."""
        log_dir = tmp_path / "new" / "log" / "dir"
        metadata = {"invocation_type": "consolidation-critic", "round": 1}
        log_path = log_session(log_dir, metadata)
        assert log_path.exists()
