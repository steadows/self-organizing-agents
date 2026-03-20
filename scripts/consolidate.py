"""Consolidation loop orchestrator for self-organizing-agents experiment.

Orchestrates the critic/defender/synthesizer debate pattern. Each round:
1. Loads current rules, task outputs, and judge scores
2. Invokes critic agent to identify rule gaps
3. Invokes defender agent to challenge proposed changes
4. Invokes synthesizer agent to produce concrete rule diffs
5. Writes debate transcript and proposal for human review

The orchestrator STOPS after producing a proposal — it does NOT apply changes.
Human approval is required before rules are modified.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")

CONSOLIDATION_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192


def load_rules(rules_dir: Path) -> dict[str, str]:
    """Load all markdown rule files from a directory.

    Args:
        rules_dir: Path to the rules directory (e.g., rules/v0/).

    Returns:
        Dict mapping filename to file content.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    rules_dir = Path(rules_dir)
    if not rules_dir.exists():
        raise FileNotFoundError(f"Rules directory not found: {rules_dir}")

    return {
        f.name: f.read_text()
        for f in sorted(rules_dir.iterdir())
        if f.is_file() and f.suffix == ".md"
    }


def load_outputs(output_dir: Path) -> dict[str, str]:
    """Load task outputs from an output directory.

    Each subdirectory is a task. All .py files within are concatenated.

    Args:
        output_dir: Path to the round output directory (e.g., outputs/evolved/round-01/).

    Returns:
        Dict mapping task_id to concatenated Python file contents.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    results: dict[str, str] = {}
    for task_dir in sorted(output_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        py_files = sorted(task_dir.glob("*.py"))
        contents = []
        for py_file in py_files:
            contents.append(f"# --- {py_file.name} ---\n{py_file.read_text()}")
        results[task_dir.name] = "\n\n".join(contents)

    return results


def load_scores(scores_dir: Path) -> dict[str, dict[str, Any]]:
    """Load judge score JSON files from a directory.

    Args:
        scores_dir: Path to the scores directory.

    Returns:
        Dict mapping task_id (from filename stem) to parsed score dict.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    scores_dir = Path(scores_dir)
    if not scores_dir.exists():
        raise FileNotFoundError(f"Scores directory not found: {scores_dir}")

    return {
        f.stem: json.loads(f.read_text())
        for f in sorted(scores_dir.iterdir())
        if f.is_file() and f.suffix == ".json"
    }


def build_critic_prompt(
    prompt_path: Path,
    rules: dict[str, str],
    outputs: dict[str, str],
    scores: dict[str, dict[str, Any]],
) -> str:
    """Assemble the full critic agent prompt.

    Args:
        prompt_path: Path to the critic prompt template.
        rules: Dict of rule filename -> content.
        outputs: Dict of task_id -> concatenated code.
        scores: Dict of task_id -> score dict.

    Returns:
        Assembled prompt string.
    """
    template = Path(prompt_path).read_text()

    rules_section = "\n\n".join(
        f"### {name}\n\n{content}" for name, content in sorted(rules.items())
    )

    outputs_section = "\n\n".join(
        f"### {task_id}\n\n```python\n{code}\n```"
        for task_id, code in sorted(outputs.items())
    )

    scores_section = "\n\n".join(
        f"### {task_id}\n\n```json\n{json.dumps(score, indent=2)}\n```"
        for task_id, score in sorted(scores.items())
    )

    return (
        f"{template}\n\n"
        f"---\n\n"
        f"## Current Rules\n\n{rules_section}\n\n"
        f"---\n\n"
        f"## Task Outputs\n\n{outputs_section}\n\n"
        f"---\n\n"
        f"## Judge Scores\n\n{scores_section}"
    )


def build_defender_prompt(
    prompt_path: Path,
    rules: dict[str, str],
    critic_response: str,
    scores: dict[str, dict[str, Any]],
) -> str:
    """Assemble the full defender agent prompt.

    Args:
        prompt_path: Path to the defender prompt template.
        rules: Dict of rule filename -> content.
        critic_response: The critic agent's full output.
        scores: Dict of task_id -> score dict.

    Returns:
        Assembled prompt string.
    """
    template = Path(prompt_path).read_text()

    rules_section = "\n\n".join(
        f"### {name}\n\n{content}" for name, content in sorted(rules.items())
    )

    scores_section = "\n\n".join(
        f"### {task_id}\n\n```json\n{json.dumps(score, indent=2)}\n```"
        for task_id, score in sorted(scores.items())
    )

    return (
        f"{template}\n\n"
        f"---\n\n"
        f"## Current Rules\n\n{rules_section}\n\n"
        f"---\n\n"
        f"## Critic's Proposals\n\n{critic_response}\n\n"
        f"---\n\n"
        f"## Judge Scores\n\n{scores_section}"
    )


def build_synthesizer_prompt(
    prompt_path: Path,
    rules: dict[str, str],
    critic_response: str,
    defender_response: str,
    scores: dict[str, dict[str, Any]],
) -> str:
    """Assemble the full synthesizer agent prompt.

    Args:
        prompt_path: Path to the synthesizer prompt template.
        rules: Dict of rule filename -> content.
        critic_response: The critic agent's full output.
        defender_response: The defender agent's full output.
        scores: Dict of task_id -> score dict.

    Returns:
        Assembled prompt string.
    """
    template = Path(prompt_path).read_text()

    rules_section = "\n\n".join(
        f"### {name}\n\n{content}" for name, content in sorted(rules.items())
    )

    scores_section = "\n\n".join(
        f"### {task_id}\n\n```json\n{json.dumps(score, indent=2)}\n```"
        for task_id, score in sorted(scores.items())
    )

    return (
        f"{template}\n\n"
        f"---\n\n"
        f"## Current Rules\n\n{rules_section}\n\n"
        f"---\n\n"
        f"## Critic's Proposals\n\n{critic_response}\n\n"
        f"---\n\n"
        f"## Defender's Responses\n\n{defender_response}\n\n"
        f"---\n\n"
        f"## Judge Scores\n\n{scores_section}"
    )


def run_agent(
    client: anthropic.Anthropic,
    model: str,
    prompt: str,
    max_tokens: int,
) -> tuple[str, dict[str, int]]:
    """Invoke a single consolidation agent via the Anthropic API.

    Args:
        client: Anthropic API client.
        model: Model identifier (e.g., claude-sonnet-4-6).
        prompt: The full assembled prompt.
        max_tokens: Maximum response tokens.

    Returns:
        Tuple of (response_text, usage_dict) where usage_dict contains
        input_tokens and output_tokens.
    """
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    return text, usage


def log_session(log_dir: Path, metadata: dict[str, Any]) -> Path:
    """Write session metadata to a JSON log file.

    Args:
        log_dir: Directory for session logs.
        metadata: Dict of session metadata to persist.

    Returns:
        Path to the written log file.
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    invocation_type = metadata.get("invocation_type", "unknown")
    round_num = metadata.get("round", 0)
    log_file = log_dir / f"{invocation_type}_round-{round_num:02d}_{timestamp}.json"

    entry = {**metadata, "timestamp": datetime.now(timezone.utc).isoformat()}
    log_file.write_text(json.dumps(entry, indent=2))
    return log_file


def run_consolidation(
    round_num: int,
    rules_dir: Path,
    output_dir: Path,
    scores_dir: Path,
    consolidation_dir: Path,
    session_log_dir: Path,
) -> dict[str, Any]:
    """Run one full consolidation round: critic -> defender -> synthesizer.

    Produces a debate transcript and a proposal file. Does NOT apply changes —
    human approval is required first.

    Args:
        round_num: The consolidation round number (1-indexed).
        rules_dir: Path to the current rules directory.
        output_dir: Path to the round's output directory.
        scores_dir: Path to the round's score directory.
        consolidation_dir: Path to the consolidation artifacts directory.
        session_log_dir: Path to the session log directory.

    Returns:
        Dict with round metadata, agent responses, and output file paths.
    """
    # Load data
    rules = load_rules(rules_dir)
    outputs = load_outputs(output_dir)
    scores = load_scores(scores_dir)

    client = anthropic.Anthropic()
    round_label = f"round-{round_num:02d}"

    # --- Critic ---
    critic_prompt = build_critic_prompt(
        prompt_path=consolidation_dir / "critic-prompt.md",
        rules=rules,
        outputs=outputs,
        scores=scores,
    )
    critic_response, critic_usage = run_agent(
        client=client,
        model=CONSOLIDATION_MODEL,
        prompt=critic_prompt,
        max_tokens=MAX_TOKENS,
    )
    log_session(session_log_dir, {
        "invocation_type": "consolidation-critic",
        "round": round_num,
        "model": CONSOLIDATION_MODEL,
        **critic_usage,
    })

    # --- Defender ---
    defender_prompt = build_defender_prompt(
        prompt_path=consolidation_dir / "defender-prompt.md",
        rules=rules,
        critic_response=critic_response,
        scores=scores,
    )
    defender_response, defender_usage = run_agent(
        client=client,
        model=CONSOLIDATION_MODEL,
        prompt=defender_prompt,
        max_tokens=MAX_TOKENS,
    )
    log_session(session_log_dir, {
        "invocation_type": "consolidation-defender",
        "round": round_num,
        "model": CONSOLIDATION_MODEL,
        **defender_usage,
    })

    # --- Synthesizer ---
    synthesizer_prompt = build_synthesizer_prompt(
        prompt_path=consolidation_dir / "synthesizer-prompt.md",
        rules=rules,
        critic_response=critic_response,
        defender_response=defender_response,
        scores=scores,
    )
    synthesizer_response, synthesizer_usage = run_agent(
        client=client,
        model=CONSOLIDATION_MODEL,
        prompt=synthesizer_prompt,
        max_tokens=MAX_TOKENS,
    )
    log_session(session_log_dir, {
        "invocation_type": "consolidation-synthesizer",
        "round": round_num,
        "model": CONSOLIDATION_MODEL,
        **synthesizer_usage,
    })

    # --- Write debate transcript ---
    debate_content = (
        f"# Consolidation Debate — Round {round_num:02d}\n\n"
        f"## Critic\n\n{critic_response}\n\n"
        f"---\n\n"
        f"## Defender\n\n{defender_response}\n\n"
        f"---\n\n"
        f"## Synthesizer\n\n{synthesizer_response}\n"
    )
    debate_file = consolidation_dir / "debates" / f"{round_label}.md"
    debate_file.write_text(debate_content)

    # --- Write proposal ---
    proposal_file = consolidation_dir / "proposals" / f"{round_label}.md"
    proposal_file.write_text(synthesizer_response)

    return {
        "round": round_num,
        "critic_response": critic_response,
        "defender_response": defender_response,
        "synthesizer_response": synthesizer_response,
        "debate_file": str(debate_file),
        "proposal_file": str(proposal_file),
    }


def main() -> None:
    """CLI entry point for the consolidation orchestrator."""
    parser = argparse.ArgumentParser(
        description="Run consolidation loop for self-organizing-agents experiment"
    )
    parser.add_argument(
        "--round", required=True, type=int, help="Consolidation round number"
    )
    parser.add_argument(
        "--rules-dir",
        default="rules/current",
        help="Path to current rules directory (default: rules/current)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Path to round output directory (e.g., outputs/evolved/round-01)",
    )
    parser.add_argument(
        "--scores-dir",
        required=True,
        help="Path to round scores directory (e.g., scores/evolved/round-01)",
    )
    parser.add_argument(
        "--consolidation-dir",
        default="consolidation",
        help="Path to consolidation artifacts (default: consolidation)",
    )
    parser.add_argument(
        "--session-log-dir",
        default="session-logs",
        help="Path to session log directory (default: session-logs)",
    )
    args = parser.parse_args()

    result = run_consolidation(
        round_num=args.round,
        rules_dir=Path(args.rules_dir),
        output_dir=Path(args.output_dir),
        scores_dir=Path(args.scores_dir),
        consolidation_dir=Path(args.consolidation_dir),
        session_log_dir=Path(args.session_log_dir),
    )

    print(json.dumps(result, indent=2))
    print(f"\nProposal written to: {result['proposal_file']}")
    print("Awaiting human approval before applying changes.")


if __name__ == "__main__":
    main()
