"""LLM-as-Judge scoring script for self-organizing-agents experiment.

Evaluates task outputs against a rubric using Claude Sonnet 4.6,
cross-checks against acceptance test results, and aggregates scores
across multiple runs using median aggregation.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")

DIMENSIONS = [
    "correctness",
    "edge_cases",
    "code_quality",
    "documentation",
    "test_coverage",
    "robustness",
]

REQUIRED_CONFIG_KEYS = {"model", "temperature", "max_tokens", "runs_per_output"}


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and validate judge configuration from a JSON file.

    Args:
        config_path: Path to the judge-config.json file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        ValueError: If required configuration keys are missing.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = json.loads(config_path.read_text())

    missing = REQUIRED_CONFIG_KEYS - set(config.keys())
    if missing:
        raise ValueError(f"Missing required config keys: {missing}")

    return config


def load_rubric(rubric_path: Path) -> str:
    """Read the judge rubric markdown file.

    Args:
        rubric_path: Path to the judge-rubric.md file.

    Returns:
        The rubric content as a string.

    Raises:
        FileNotFoundError: If the rubric file does not exist.
    """
    rubric_path = Path(rubric_path)
    if not rubric_path.exists():
        raise FileNotFoundError(f"Rubric file not found: {rubric_path}")

    return rubric_path.read_text()


def read_output(output_dir: Path) -> dict[str, str]:
    """Read Python implementation and test files from an output directory.

    Args:
        output_dir: Path to the directory containing task output files.

    Returns:
        Dictionary mapping filenames to their contents (Python files only).

    Raises:
        FileNotFoundError: If the output directory does not exist.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    files: dict[str, str] = {}
    for py_file in sorted(output_dir.glob("*.py")):
        files[py_file.name] = py_file.read_text()

    return files


def run_acceptance_tests(
    test_file: Path, output_dir: Path
) -> dict[str, Any]:
    """Run acceptance tests against task output using pytest.

    Args:
        test_file: Path to the acceptance test file.
        output_dir: Path to the output directory (added to PYTHONPATH).

    Returns:
        Dictionary with keys: total, passed, failed, all_passed, details.
    """
    test_file = Path(test_file)
    output_dir = Path(output_dir)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-v",
            "--tb=short",
            f"--rootdir={output_dir}",
        ],
        capture_output=True,
        text=True,
        env={
            **__import__("os").environ,
            "PYTHONPATH": str(output_dir),
        },
        timeout=60,
    )

    stdout = result.stdout
    passed = len(re.findall(r" PASSED", stdout))
    failed = len(re.findall(r" FAILED", stdout))
    total = passed + failed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "all_passed": failed == 0 and passed > 0,
        "details": stdout,
    }


def parse_scores(llm_response: str) -> dict[str, dict[str, Any]]:
    """Parse the 6-dimension JSON scores from an LLM response.

    Handles both raw JSON and JSON embedded in markdown code blocks.

    Args:
        llm_response: The raw text response from the LLM.

    Returns:
        Dictionary mapping dimension names to score/justification dicts.

    Raises:
        json.JSONDecodeError: If no valid JSON is found.
        ValueError: If dimensions are missing or scores are out of range.
    """
    # Try to extract JSON from markdown code block first
    code_block_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", llm_response, re.DOTALL)
    json_str = code_block_match.group(1) if code_block_match else llm_response

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        # Try the full response if code block extraction failed
        data = json.loads(llm_response)

    scores = data.get("scores", data)

    missing = set(DIMENSIONS) - set(scores.keys())
    if missing:
        raise ValueError(f"Missing score dimensions: {missing}")

    for dim in DIMENSIONS:
        score_val = scores[dim]["score"]
        if not (1 <= score_val <= 10):
            raise ValueError(
                f"Score for '{dim}' is out of range (1-10): {score_val}"
            )

    return {dim: scores[dim] for dim in DIMENSIONS}


def cap_scores(
    scores: dict[str, dict[str, Any]], *, acceptance_passed: bool
) -> dict[str, dict[str, Any]]:
    """Cap correctness and edge_cases scores if acceptance tests failed.

    Returns a new dict — does not mutate the original.

    Args:
        scores: The score dictionary for all 6 dimensions.
        acceptance_passed: Whether all acceptance tests passed.

    Returns:
        A new score dictionary with capped values where applicable.
    """
    result = copy.deepcopy(scores)

    if not acceptance_passed:
        for dim in ("correctness", "edge_cases"):
            if result[dim]["score"] > 5:
                result[dim]["score"] = 5

    return result


def compute_median_scores(
    runs: list[dict[str, dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """Compute median score per dimension across multiple runs.

    Selects the justification from the run whose score equals the median.

    Args:
        runs: List of score dictionaries (one per run).

    Returns:
        A single score dictionary with median scores per dimension.
    """
    result: dict[str, dict[str, Any]] = {}

    for dim in DIMENSIONS:
        dim_scores = [run[dim]["score"] for run in runs]
        median_val = statistics.median(dim_scores)

        # Find the run whose score matches the median for justification
        justification = runs[0][dim]["justification"]
        for run in runs:
            if run[dim]["score"] == median_val:
                justification = run[dim]["justification"]
                break

        result[dim] = {"score": median_val, "justification": justification}

    return result


def log_session(log_dir: Path, metadata: dict[str, Any]) -> Path:
    """Write session metadata to a JSON log file.

    Args:
        log_dir: Directory to write the log file to.
        metadata: Session metadata dictionary.

    Returns:
        Path to the written log file.
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    task_id = metadata.get("task_id", "unknown")
    log_file = log_dir / f"judge_{task_id}_{timestamp}.json"

    log_file.write_text(json.dumps(metadata, indent=2))
    return log_file


def _build_prompt(
    rubric: str,
    output_files: dict[str, str],
    acceptance_results: dict[str, Any],
    task_id: str,
) -> str:
    """Build the prompt for the LLM judge.

    Args:
        rubric: The scoring rubric text.
        output_files: Dictionary of filename -> content.
        acceptance_results: Results from running acceptance tests.
        task_id: The task identifier.

    Returns:
        Formatted prompt string.
    """
    files_section = "\n\n".join(
        f"### {name}\n```python\n{content}\n```"
        for name, content in sorted(output_files.items())
    )

    acceptance_summary = (
        f"Passed: {acceptance_results['passed']}/{acceptance_results['total']}, "
        f"Failed: {acceptance_results['failed']}/{acceptance_results['total']}, "
        f"All passed: {acceptance_results['all_passed']}"
    )

    return (
        f"You are a code quality judge. Score the following task output "
        f"according to the rubric.\n\n"
        f"## Task ID: {task_id}\n\n"
        f"## Rubric\n{rubric}\n\n"
        f"## Acceptance Test Results\n{acceptance_summary}\n\n"
        f"## Output Files\n{files_section}\n\n"
        f"Return your scores as JSON matching the rubric's output format."
    )


def judge_output(
    task_id: str,
    output_dir: Path,
    acceptance_test_file: Path,
    config_path: Path,
    rubric_path: Path,
    scores_dir: Path,
    session_log_dir: Path,
) -> dict[str, Any]:
    """Orchestrate the full judging flow for a single task output.

    Runs acceptance tests, calls the LLM 3 times, computes median scores,
    applies caps, writes results, and logs the session.

    Args:
        task_id: Identifier for the task being judged.
        output_dir: Directory containing the task output files.
        acceptance_test_file: Path to the acceptance test file.
        config_path: Path to judge-config.json.
        rubric_path: Path to judge-rubric.md.
        scores_dir: Directory to write the final score JSON.
        session_log_dir: Directory to write session logs.

    Returns:
        The final result dictionary with scores and metadata.
    """
    config = load_config(config_path)
    rubric = load_rubric(rubric_path)
    output_files = read_output(output_dir)
    acceptance_results = run_acceptance_tests(acceptance_test_file, output_dir)

    prompt = _build_prompt(rubric, output_files, acceptance_results, task_id)

    client = anthropic.Anthropic()
    runs_per_output = config.get("runs_per_output", 3)

    all_runs: list[dict[str, dict[str, Any]]] = []
    total_input_tokens = 0
    total_output_tokens = 0

    for _ in range(runs_per_output):
        response = client.messages.create(
            model=config["model"],
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
            messages=[{"role": "user", "content": prompt}],
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        llm_text = response.content[0].text
        scores = parse_scores(llm_text)
        capped = cap_scores(scores, acceptance_passed=acceptance_results["all_passed"])
        all_runs.append(capped)

    median_scores = compute_median_scores(all_runs)

    # Compute overall as arithmetic mean rounded to 1 decimal
    overall = round(
        statistics.mean(median_scores[dim]["score"] for dim in DIMENSIONS), 1
    )

    result = {
        "task_id": task_id,
        "scores": median_scores,
        "overall": overall,
        "acceptance_test_pass": acceptance_results["all_passed"],
        "acceptance_test_details": (
            f"{acceptance_results['passed']}/{acceptance_results['total']} passed"
        ),
        "runs": runs_per_output,
        "aggregation": "median",
    }

    # Write results to scores directory
    scores_dir = Path(scores_dir)
    scores_dir.mkdir(parents=True, exist_ok=True)
    result_file = scores_dir / f"{task_id}.json"
    result_file.write_text(json.dumps(result, indent=2))

    # Log session metadata
    # Estimate cost: Sonnet 4 pricing ~$3/M input, $15/M output
    estimated_cost = (total_input_tokens * 3.0 / 1_000_000) + (
        total_output_tokens * 15.0 / 1_000_000
    )

    session_metadata = {
        "model": config["model"],
        "task_id": task_id,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "estimated_cost_usd": round(estimated_cost, 4),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runs": runs_per_output,
    }
    log_session(session_log_dir, session_metadata)

    return result


def main() -> None:
    """CLI entry point for the judge script."""
    parser = argparse.ArgumentParser(
        description="LLM-as-Judge scoring for self-organizing-agents"
    )
    parser.add_argument("--task", required=True, help="Task ID (e.g. task-001)")
    parser.add_argument("--output-dir", required=True, help="Path to task output directory")
    parser.add_argument(
        "--acceptance-test", required=True, help="Path to acceptance test file"
    )
    parser.add_argument(
        "--config",
        default="scores/judge-config.json",
        help="Path to judge config (default: scores/judge-config.json)",
    )
    parser.add_argument(
        "--rubric",
        default="scores/judge-rubric.md",
        help="Path to judge rubric (default: scores/judge-rubric.md)",
    )
    parser.add_argument(
        "--scores-dir",
        default="scores",
        help="Directory to write score results (default: scores)",
    )
    parser.add_argument(
        "--session-log-dir",
        default="session-logs",
        help="Directory for session logs (default: session-logs)",
    )
    args = parser.parse_args()

    result = judge_output(
        task_id=args.task,
        output_dir=Path(args.output_dir),
        acceptance_test_file=Path(args.acceptance_test),
        config_path=Path(args.config),
        rubric_path=Path(args.rubric),
        scores_dir=Path(args.scores_dir),
        session_log_dir=Path(args.session_log_dir),
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
