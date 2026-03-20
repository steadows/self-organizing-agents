"""Task executor script for self-organizing-agents experiment.

Orchestrates running a single task via the Claude API: reads rules and
task spec, calls the model, parses code blocks from the response, and
writes implementation files to the output directory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic

MODEL = "claude-opus-4-6"
TEMPERATURE = 1.0
MAX_TOKENS = 8192

# Opus 4 pricing: $15/MTok input, $75/MTok output
INPUT_COST_PER_MTOK = 15.0
OUTPUT_COST_PER_MTOK = 75.0


def load_rules(rules_dir: Path) -> str:
    """Read and concatenate all markdown rule files from a directory.

    Args:
        rules_dir: Path to the directory containing rule .md files.

    Returns:
        Combined rules content as a single string.

    Raises:
        FileNotFoundError: If the rules directory does not exist.
        ValueError: If no .md files are found in the directory.
    """
    rules_dir = Path(rules_dir)
    if not rules_dir.exists():
        raise FileNotFoundError(f"Rules directory not found: {rules_dir}")

    rule_files = sorted(rules_dir.glob("*.md"))
    if not rule_files:
        raise ValueError(f"No .md files found in rules directory: {rules_dir}")

    sections: list[str] = []
    for rule_file in rule_files:
        content = rule_file.read_text()
        sections.append(f"## {rule_file.stem}\n\n{content}")

    return "\n\n---\n\n".join(sections)


def load_task_spec(task_spec_path: Path) -> str:
    """Read a task specification markdown file.

    Args:
        task_spec_path: Path to the task spec .md file.

    Returns:
        The task spec content as a string.

    Raises:
        FileNotFoundError: If the task spec file does not exist.
    """
    task_spec_path = Path(task_spec_path)
    if not task_spec_path.exists():
        raise FileNotFoundError(f"Task spec not found: {task_spec_path}")

    return task_spec_path.read_text()


def derive_task_id(task_spec_path: Path) -> str:
    """Derive the task ID from a task spec filename.

    Args:
        task_spec_path: Path to the task spec file.

    Returns:
        The task ID string (e.g., 'task-001' from 'task-001.md').
    """
    return Path(task_spec_path).stem


def parse_code_blocks(response_text: str) -> dict[str, str]:
    """Extract named code blocks from an LLM response.

    Expects code blocks with filenames in the info string, e.g.:
        ```python slugify.py
        def slugify(...): ...
        ```

    Args:
        response_text: The raw text response from the LLM.

    Returns:
        Dictionary mapping filenames to code content.

    Raises:
        ValueError: If no code blocks with filenames are found.
    """
    pattern = r"```python\s+([\w\-./]+\.py)\s*\n(.*?)```"
    matches = re.findall(pattern, response_text, re.DOTALL)

    if not matches:
        raise ValueError(
            "No code blocks with filenames found in the response. "
            "Expected format: ```python filename.py"
        )

    files: dict[str, str] = {}
    for filename, content in matches:
        # Strip trailing whitespace but preserve internal structure
        files[filename] = content.rstrip() + "\n"

    return files


def write_output_files(output_dir: Path, files: dict[str, str]) -> list[Path]:
    """Write extracted code files to the output directory.

    Args:
        output_dir: Directory to write files to (created if needed).
        files: Dictionary mapping filenames to code content.

    Returns:
        List of paths to written files.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for filename, content in files.items():
        file_path = output_dir / filename
        file_path.write_text(content)
        written.append(file_path)

    return written


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
    log_file = log_dir / f"executor_{task_id}_{timestamp}.json"

    log_file.write_text(json.dumps(metadata, indent=2))
    return log_file


def run_task(
    task_spec_path: Path,
    rules_dir: Path,
    output_dir: Path,
    session_log_dir: Path,
) -> dict[str, Any]:
    """Orchestrate the full task execution flow.

    Loads rules and task spec, calls the Claude API, parses code blocks
    from the response, writes output files, and logs session metadata.

    Args:
        task_spec_path: Path to the task spec markdown file.
        rules_dir: Path to the directory containing rule .md files.
        output_dir: Directory to write implementation files to.
        session_log_dir: Directory to write session logs to.

    Returns:
        Dictionary with task_id, model, files_written, and token usage.

    Raises:
        anthropic.APIError: If the API call fails.
        ValueError: If no code blocks are found in the response.
    """
    task_id = derive_task_id(task_spec_path)
    rules_content = load_rules(rules_dir)
    task_spec = load_task_spec(task_spec_path)

    system_prompt = (
        "You are a Python developer implementing utility functions. "
        f"Follow these rules:\n\n{rules_content}"
    )

    user_message = (
        "Implement the following task. Return ONLY the Python files — "
        "the implementation file and a test file. Use markdown code blocks "
        "with the filename as the info string (e.g., ```python slugify.py). "
        f"Do not include any other text.\n\n{task_spec}"
    )

    client = anthropic.Anthropic()

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    response_text = response.content[0].text

    files = parse_code_blocks(response_text)
    written_paths = write_output_files(output_dir, files)

    estimated_cost = (input_tokens * INPUT_COST_PER_MTOK / 1_000_000) + (
        output_tokens * OUTPUT_COST_PER_MTOK / 1_000_000
    )

    session_metadata = {
        "invocation_type": "executor",
        "model": MODEL,
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(estimated_cost, 4),
    }
    log_path = log_session(session_log_dir, session_metadata)

    result = {
        "task_id": task_id,
        "model": MODEL,
        "files_written": [str(p) for p in written_paths],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(estimated_cost, 4),
        "session_log": str(log_path),
    }

    return result


def main() -> None:
    """CLI entry point for the task executor script."""
    parser = argparse.ArgumentParser(
        description="Run a single task via the Claude API"
    )
    parser.add_argument(
        "--task-spec",
        required=True,
        help="Path to the task spec markdown file (e.g., tasks/task-001.md)",
    )
    parser.add_argument(
        "--rules-dir",
        required=True,
        help="Path to the rules directory (e.g., rules/current/)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Where to write the implementation (e.g., outputs/baseline/task-001/)",
    )
    parser.add_argument(
        "--session-log-dir",
        default="session-logs",
        help="Where to write session metadata (default: session-logs/)",
    )
    args = parser.parse_args()

    result = run_task(
        task_spec_path=Path(args.task_spec),
        rules_dir=Path(args.rules_dir),
        output_dir=Path(args.output_dir),
        session_log_dir=Path(args.session_log_dir),
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
