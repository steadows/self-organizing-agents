"""Tests for the LLM-as-Judge scoring script."""

import json
import statistics
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import will fail until judge.py is implemented (RED phase)
from scripts.judge import (
    cap_scores,
    compute_median_scores,
    judge_output,
    load_config,
    load_rubric,
    log_session,
    parse_scores,
    read_output,
    run_acceptance_tests,
)

DIMENSIONS = [
    "correctness",
    "edge_cases",
    "code_quality",
    "documentation",
    "test_coverage",
    "robustness",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Create a minimal project structure for testing."""
    scores_dir = tmp_path / "scores"
    scores_dir.mkdir()

    config = {
        "model": "claude-sonnet-4-6",
        "temperature": 0.0,
        "max_tokens": 4096,
        "rubric_file": "scores/judge-rubric.md",
        "runs_per_output": 3,
        "aggregation": "median",
        "frozen": True,
        "frozen_date": "2026-03-20",
    }
    (scores_dir / "judge-config.json").write_text(json.dumps(config))
    (scores_dir / "judge-rubric.md").write_text("# Rubric\nScore each dimension 1-10.\n")
    return tmp_path


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create a sample output directory with implementation and test files."""
    out = tmp_path / "output"
    out.mkdir()
    (out / "solution.py").write_text("def add(a, b):\n    return a + b\n")
    (out / "test_solution.py").write_text(
        "def test_add():\n    assert add(1, 2) == 3\n"
    )
    return out


@pytest.fixture
def acceptance_test_file(tmp_path: Path) -> Path:
    """Create a simple acceptance test file."""
    test_file = tmp_path / "test_acceptance.py"
    test_file.write_text(
        "def test_pass():\n    assert True\n\ndef test_also_pass():\n    assert True\n"
    )
    return test_file


@pytest.fixture
def sample_scores() -> dict:
    """Return a valid score dict for all 6 dimensions."""
    return {
        dim: {"score": 8, "justification": f"Good {dim}"}
        for dim in DIMENSIONS
    }


@pytest.fixture
def sample_llm_response(sample_scores: dict) -> str:
    """Return a sample LLM JSON response string."""
    payload = {
        "task_id": "task-001",
        "scores": sample_scores,
        "overall": 8.0,
        "acceptance_test_pass": True,
        "acceptance_test_details": "2/2 passed",
    }
    return json.dumps(payload)


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

class TestLoadConfig:
    """Tests for load_config()."""

    def test_loads_valid_config(self, project_root: Path) -> None:
        config_path = project_root / "scores" / "judge-config.json"
        config = load_config(config_path)
        assert config["model"] == "claude-sonnet-4-6"
        assert config["temperature"] == 0.0
        assert config["runs_per_output"] == 3

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "nonexistent.json")

    def test_raises_on_invalid_json(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json at all")
        with pytest.raises(json.JSONDecodeError):
            load_config(bad_file)

    def test_raises_on_missing_required_keys(self, tmp_path: Path) -> None:
        incomplete = tmp_path / "incomplete.json"
        incomplete.write_text(json.dumps({"model": "x"}))
        with pytest.raises(ValueError, match="Missing required config keys"):
            load_config(incomplete)


# ---------------------------------------------------------------------------
# load_rubric
# ---------------------------------------------------------------------------

class TestLoadRubric:
    """Tests for load_rubric()."""

    def test_loads_rubric_content(self, project_root: Path) -> None:
        rubric_path = project_root / "scores" / "judge-rubric.md"
        rubric = load_rubric(rubric_path)
        assert "Rubric" in rubric
        assert "1-10" in rubric

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_rubric(tmp_path / "nonexistent.md")


# ---------------------------------------------------------------------------
# read_output
# ---------------------------------------------------------------------------

class TestReadOutput:
    """Tests for read_output()."""

    def test_reads_implementation_and_tests(self, output_dir: Path) -> None:
        result = read_output(output_dir)
        assert "solution.py" in result
        assert "def add" in result["solution.py"]
        assert "test_solution.py" in result
        assert "test_add" in result["test_solution.py"]

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_output(tmp_path / "nonexistent")

    def test_reads_only_python_files(self, output_dir: Path) -> None:
        (output_dir / "README.md").write_text("# Readme")
        (output_dir / "data.txt").write_text("some data")
        result = read_output(output_dir)
        assert "README.md" not in result
        assert "data.txt" not in result
        assert "solution.py" in result


# ---------------------------------------------------------------------------
# run_acceptance_tests
# ---------------------------------------------------------------------------

class TestRunAcceptanceTests:
    """Tests for run_acceptance_tests()."""

    def test_all_tests_pass(self, acceptance_test_file: Path, output_dir: Path) -> None:
        results = run_acceptance_tests(acceptance_test_file, output_dir)
        assert results["passed"] >= 1
        assert results["failed"] == 0
        assert results["all_passed"] is True

    def test_failing_tests_detected(self, tmp_path: Path, output_dir: Path) -> None:
        failing_test = tmp_path / "test_fail.py"
        failing_test.write_text(
            "def test_should_fail():\n    assert False\n\n"
            "def test_should_pass():\n    assert True\n"
        )
        results = run_acceptance_tests(failing_test, output_dir)
        assert results["failed"] >= 1
        assert results["all_passed"] is False

    def test_returns_test_details(self, acceptance_test_file: Path, output_dir: Path) -> None:
        results = run_acceptance_tests(acceptance_test_file, output_dir)
        assert "total" in results
        assert "passed" in results
        assert "failed" in results
        assert "all_passed" in results


# ---------------------------------------------------------------------------
# parse_scores
# ---------------------------------------------------------------------------

class TestParseScores:
    """Tests for parse_scores()."""

    def test_parses_valid_response(self, sample_llm_response: str) -> None:
        scores = parse_scores(sample_llm_response)
        for dim in DIMENSIONS:
            assert dim in scores
            assert 1 <= scores[dim]["score"] <= 10

    def test_raises_on_invalid_json(self) -> None:
        with pytest.raises((json.JSONDecodeError, ValueError)):
            parse_scores("not json")

    def test_raises_on_missing_dimensions(self) -> None:
        partial = json.dumps({
            "scores": {"correctness": {"score": 5, "justification": "ok"}}
        })
        with pytest.raises(ValueError, match="Missing.*dimensions"):
            parse_scores(partial)

    def test_raises_on_score_out_of_range(self) -> None:
        bad_scores = {
            dim: {"score": 8, "justification": "ok"}
            for dim in DIMENSIONS
        }
        bad_scores["correctness"]["score"] = 11
        response = json.dumps({"scores": bad_scores})
        with pytest.raises(ValueError, match="out of range"):
            parse_scores(response)

    def test_raises_on_score_below_range(self) -> None:
        bad_scores = {
            dim: {"score": 8, "justification": "ok"}
            for dim in DIMENSIONS
        }
        bad_scores["robustness"]["score"] = 0
        response = json.dumps({"scores": bad_scores})
        with pytest.raises(ValueError, match="out of range"):
            parse_scores(response)

    def test_extracts_json_from_markdown_code_block(self) -> None:
        scores_dict = {
            dim: {"score": 7, "justification": "decent"}
            for dim in DIMENSIONS
        }
        payload = json.dumps({"scores": scores_dict})
        wrapped = f"Here are the scores:\n```json\n{payload}\n```\n"
        scores = parse_scores(wrapped)
        assert scores["correctness"]["score"] == 7


# ---------------------------------------------------------------------------
# cap_scores
# ---------------------------------------------------------------------------

class TestCapScores:
    """Tests for cap_scores()."""

    def test_no_cap_when_acceptance_passed(self, sample_scores: dict) -> None:
        capped = cap_scores(sample_scores, acceptance_passed=True)
        assert capped["correctness"]["score"] == 8
        assert capped["edge_cases"]["score"] == 8

    def test_caps_correctness_when_acceptance_failed(self, sample_scores: dict) -> None:
        capped = cap_scores(sample_scores, acceptance_passed=False)
        assert capped["correctness"]["score"] <= 5
        assert capped["edge_cases"]["score"] <= 5

    def test_does_not_cap_other_dimensions(self, sample_scores: dict) -> None:
        capped = cap_scores(sample_scores, acceptance_passed=False)
        assert capped["code_quality"]["score"] == 8
        assert capped["documentation"]["score"] == 8
        assert capped["test_coverage"]["score"] == 8
        assert capped["robustness"]["score"] == 8

    def test_does_not_modify_original(self, sample_scores: dict) -> None:
        original_correctness = sample_scores["correctness"]["score"]
        cap_scores(sample_scores, acceptance_passed=False)
        assert sample_scores["correctness"]["score"] == original_correctness

    def test_leaves_low_scores_unchanged(self) -> None:
        scores = {
            dim: {"score": 3, "justification": "poor"}
            for dim in DIMENSIONS
        }
        capped = cap_scores(scores, acceptance_passed=False)
        assert capped["correctness"]["score"] == 3
        assert capped["edge_cases"]["score"] == 3


# ---------------------------------------------------------------------------
# compute_median_scores
# ---------------------------------------------------------------------------

class TestComputeMedianScores:
    """Tests for compute_median_scores()."""

    def test_median_of_three_runs(self) -> None:
        runs = [
            {dim: {"score": s, "justification": "j"} for dim, s in zip(DIMENSIONS, [7, 8, 6, 5, 9, 7])},
            {dim: {"score": s, "justification": "j"} for dim, s in zip(DIMENSIONS, [8, 7, 7, 6, 8, 8])},
            {dim: {"score": s, "justification": "j"} for dim, s in zip(DIMENSIONS, [9, 9, 8, 7, 7, 9])},
        ]
        median_scores = compute_median_scores(runs)
        assert median_scores["correctness"]["score"] == 8
        assert median_scores["edge_cases"]["score"] == 8
        assert median_scores["code_quality"]["score"] == 7

    def test_single_run(self) -> None:
        run = {dim: {"score": 5, "justification": "ok"} for dim in DIMENSIONS}
        median_scores = compute_median_scores([run])
        for dim in DIMENSIONS:
            assert median_scores[dim]["score"] == 5

    def test_preserves_justification_from_median_run(self) -> None:
        runs = [
            {dim: {"score": 5, "justification": "low"} for dim in DIMENSIONS},
            {dim: {"score": 7, "justification": "mid"} for dim in DIMENSIONS},
            {dim: {"score": 9, "justification": "high"} for dim in DIMENSIONS},
        ]
        median_scores = compute_median_scores(runs)
        # Median score is 7, so justification should come from the run with score 7
        for dim in DIMENSIONS:
            assert median_scores[dim]["score"] == 7
            assert median_scores[dim]["justification"] == "mid"


# ---------------------------------------------------------------------------
# judge_output (full orchestration — mocked)
# ---------------------------------------------------------------------------

class TestJudgeOutput:
    """Tests for judge_output() with mocked API calls."""

    def _make_llm_response(self, scores: dict) -> str:
        return json.dumps({
            "scores": scores,
            "overall": 7.0,
            "acceptance_test_pass": True,
            "acceptance_test_details": "2/2 passed",
        })

    @patch("scripts.judge.anthropic")
    def test_orchestrates_full_flow(
        self,
        mock_anthropic_module: MagicMock,
        project_root: Path,
        output_dir: Path,
        acceptance_test_file: Path,
        sample_scores: dict,
    ) -> None:
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=self._make_llm_response(sample_scores))]
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 500
        mock_client.messages.create.return_value = mock_response

        scores_output_dir = project_root / "scores"
        session_log_dir = project_root / "session-logs"
        session_log_dir.mkdir(exist_ok=True)

        result = judge_output(
            task_id="task-001",
            output_dir=output_dir,
            acceptance_test_file=acceptance_test_file,
            config_path=project_root / "scores" / "judge-config.json",
            rubric_path=project_root / "scores" / "judge-rubric.md",
            scores_dir=scores_output_dir,
            session_log_dir=session_log_dir,
        )

        assert "scores" in result
        for dim in DIMENSIONS:
            assert dim in result["scores"]
        assert mock_client.messages.create.call_count == 3  # 3 runs

    @patch("scripts.judge.anthropic")
    def test_caps_scores_when_acceptance_fails(
        self,
        mock_anthropic_module: MagicMock,
        project_root: Path,
        output_dir: Path,
        tmp_path: Path,
    ) -> None:
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client

        high_scores = {
            dim: {"score": 9, "justification": "great"} for dim in DIMENSIONS
        }
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=self._make_llm_response(high_scores))]
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 500
        mock_client.messages.create.return_value = mock_response

        failing_test = tmp_path / "test_fail_acceptance.py"
        failing_test.write_text("def test_fails():\n    assert False\n")

        session_log_dir = project_root / "session-logs"
        session_log_dir.mkdir(exist_ok=True)

        result = judge_output(
            task_id="task-002",
            output_dir=output_dir,
            acceptance_test_file=failing_test,
            config_path=project_root / "scores" / "judge-config.json",
            rubric_path=project_root / "scores" / "judge-rubric.md",
            scores_dir=project_root / "scores",
            session_log_dir=session_log_dir,
        )

        assert result["scores"]["correctness"]["score"] <= 5
        assert result["scores"]["edge_cases"]["score"] <= 5

    @patch("scripts.judge.anthropic")
    def test_writes_results_to_scores_dir(
        self,
        mock_anthropic_module: MagicMock,
        project_root: Path,
        output_dir: Path,
        acceptance_test_file: Path,
        sample_scores: dict,
    ) -> None:
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=self._make_llm_response(sample_scores))]
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 500
        mock_client.messages.create.return_value = mock_response

        scores_output_dir = project_root / "scores"
        session_log_dir = project_root / "session-logs"
        session_log_dir.mkdir(exist_ok=True)

        judge_output(
            task_id="task-001",
            output_dir=output_dir,
            acceptance_test_file=acceptance_test_file,
            config_path=project_root / "scores" / "judge-config.json",
            rubric_path=project_root / "scores" / "judge-rubric.md",
            scores_dir=scores_output_dir,
            session_log_dir=session_log_dir,
        )

        result_file = scores_output_dir / "task-001.json"
        assert result_file.exists()
        data = json.loads(result_file.read_text())
        assert "scores" in data


# ---------------------------------------------------------------------------
# log_session
# ---------------------------------------------------------------------------

class TestLogSession:
    """Tests for log_session()."""

    def test_writes_session_log(self, tmp_path: Path) -> None:
        log_dir = tmp_path / "session-logs"
        log_dir.mkdir()
        metadata = {
            "model": "claude-sonnet-4-6",
            "input_tokens": 1000,
            "output_tokens": 500,
            "estimated_cost_usd": 0.012,
            "timestamp": "2026-03-20T12:00:00Z",
            "task_id": "task-001",
        }
        log_session(log_dir, metadata)
        log_files = list(log_dir.glob("*.json"))
        assert len(log_files) == 1
        data = json.loads(log_files[0].read_text())
        assert data["model"] == "claude-sonnet-4-6"
        assert data["task_id"] == "task-001"

    def test_creates_log_dir_if_missing(self, tmp_path: Path) -> None:
        log_dir = tmp_path / "new-session-logs"
        metadata = {
            "model": "claude-sonnet-4-6",
            "input_tokens": 100,
            "output_tokens": 50,
            "estimated_cost_usd": 0.001,
            "timestamp": "2026-03-20T12:00:00Z",
            "task_id": "task-001",
        }
        log_session(log_dir, metadata)
        assert log_dir.exists()
        assert len(list(log_dir.glob("*.json"))) == 1
