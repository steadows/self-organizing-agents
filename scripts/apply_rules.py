"""Rule applicator for self-organizing-agents experiment.

Reads an approved consolidation proposal, validates it against safety
constraints, copies current rules to a new version directory, applies
changes, and updates the symlink. Rolls back on any validation failure.

Safety validations:
- Rule files must stay under 150 lines
- No executable code blocks (bash, python, sh)
- Max 2 of 3 rule files modified per round
- Max 20 net new lines per rule file per round
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

MAX_LINES_PER_FILE = 150
MAX_NET_NEW_LINES_PER_FILE = 20
MAX_FILES_MODIFIED = 2
EXECUTABLE_BLOCK_PATTERN = re.compile(
    r"```(?:python|bash|sh|shell|zsh)\b", re.IGNORECASE
)


def validate_line_count(file_path: Path) -> None:
    """Validate that a rule file does not exceed the line limit.

    Args:
        file_path: Path to the rule file.

    Raises:
        ValueError: If the file exceeds MAX_LINES_PER_FILE lines.
    """
    line_count = len(Path(file_path).read_text().splitlines())
    if line_count > MAX_LINES_PER_FILE:
        raise ValueError(
            f"Rule file {file_path.name} has {line_count} lines, "
            f"exceeding the {MAX_LINES_PER_FILE}-line limit"
        )


def validate_no_executable_blocks(file_path: Path) -> None:
    """Validate that a rule file contains no executable code blocks.

    Args:
        file_path: Path to the rule file.

    Raises:
        ValueError: If the file contains executable code fenced blocks.
    """
    content = Path(file_path).read_text()
    match = EXECUTABLE_BLOCK_PATTERN.search(content)
    if match:
        raise ValueError(
            f"Rule file {file_path.name} contains executable code block: "
            f"{match.group()!r}"
        )


def validate_change_scope(net_new_lines: dict[str, int]) -> None:
    """Validate that net new lines per file stay within the cap.

    Args:
        net_new_lines: Dict mapping filename to net new line count.

    Raises:
        ValueError: If any file exceeds MAX_NET_NEW_LINES_PER_FILE.
    """
    for filename, count in net_new_lines.items():
        if count > MAX_NET_NEW_LINES_PER_FILE:
            raise ValueError(
                f"File {filename} has {count} net new lines, "
                f"exceeding the {MAX_NET_NEW_LINES_PER_FILE}-line cap"
            )


def validate_file_count(files_modified: list[str]) -> None:
    """Validate that no more than MAX_FILES_MODIFIED files are changed.

    Args:
        files_modified: List of filenames being modified.

    Raises:
        ValueError: If more than MAX_FILES_MODIFIED files are modified.
    """
    if len(files_modified) > MAX_FILES_MODIFIED:
        raise ValueError(
            f"Proposal modifies {len(files_modified)} files, "
            f"exceeding the {MAX_FILES_MODIFIED}-file cap"
        )


def copy_rules_to_new_version(rules_base: Path, version: int) -> Path:
    """Copy the current rules to a new version directory.

    Args:
        rules_base: Path to the rules/ directory.
        version: New version number (e.g., 1 for v1).

    Returns:
        Path to the newly created version directory.

    Raises:
        FileExistsError: If the target version directory already exists.
    """
    rules_base = Path(rules_base)
    new_dir = rules_base / f"v{version}"

    if new_dir.exists():
        raise FileExistsError(f"Version directory already exists: {new_dir}")

    # Resolve the current symlink to get the source directory
    current_link = rules_base / "current"
    source_dir = current_link.resolve()

    shutil.copytree(source_dir, new_dir)
    return new_dir


def update_symlink(rules_base: Path, version: int) -> None:
    """Update the rules/current symlink to point to a new version.

    Args:
        rules_base: Path to the rules/ directory.
        version: Version number to point to (e.g., 1 for v1).
    """
    rules_base = Path(rules_base)
    current_link = rules_base / "current"

    if current_link.is_symlink():
        current_link.unlink()

    current_link.symlink_to(f"v{version}")


def apply_proposal(version_dir: Path, proposal: dict[str, Any]) -> None:
    """Apply a consolidation proposal's changes to rule files.

    Args:
        version_dir: Path to the new version directory (e.g., rules/v1/).
        proposal: Parsed proposal dict with 'changes' list.
    """
    for change in proposal["changes"]:
        file_path = (version_dir / change["file"]).resolve()
        if not str(file_path).startswith(str(version_dir.resolve())):
            raise ValueError(f"Path traversal detected: {change['file']}")
        content = file_path.read_text()

        if change["action"] == "ADD":
            after_line = change["after_line"]
            lines = content.splitlines(keepends=True)
            insert_idx = len(lines)  # default: append at end

            for i, line in enumerate(lines):
                if after_line in line:
                    insert_idx = i + 1
                    break

            new_lines = change["new_text"]
            if not new_lines.endswith("\n"):
                new_lines += "\n"

            lines.insert(insert_idx, new_lines)
            file_path.write_text("".join(lines))

        elif change["action"] == "MODIFY":
            old_text = change.get("old_text", "")
            new_text = change.get("new_text", "")
            content = content.replace(old_text, new_text)
            file_path.write_text(content)

        elif change["action"] == "DELETE":
            old_text = change.get("old_text", "")
            content = content.replace(old_text, "")
            file_path.write_text(content)


def apply_rules(
    rules_base: Path,
    version: int,
    proposal: dict[str, Any],
) -> dict[str, Any]:
    """Apply a consolidation proposal with full validation and rollback.

    This is the main entry point. It:
    1. Validates proposal scope (file count, line caps)
    2. Copies current rules to a new version directory
    3. Applies changes from the proposal
    4. Validates the result (line count, no executable blocks)
    5. Updates the symlink to the new version
    6. Rolls back on any validation failure

    Args:
        rules_base: Path to the rules/ directory.
        version: New version number (e.g., 1 for v1).
        proposal: Parsed proposal dict.

    Returns:
        Dict with version number, success status, and applied files.

    Raises:
        ValueError: If any validation fails (with rollback).
        FileExistsError: If the target version already exists.
    """
    rules_base = Path(rules_base)

    # Pre-validate scope constraints
    files_modified = proposal["summary"]["rules_modified"]
    validate_file_count(files_modified)
    validate_change_scope(proposal["summary"]["net_new_lines"])

    # Copy and apply
    new_dir = copy_rules_to_new_version(rules_base, version)

    try:
        apply_proposal(new_dir, proposal)

        # Post-validation: check every modified file
        for filename in files_modified:
            file_path = new_dir / filename
            validate_line_count(file_path)
            validate_no_executable_blocks(file_path)

        # All validations passed — update symlink
        update_symlink(rules_base, version)

        return {
            "version": version,
            "success": True,
            "version_dir": str(new_dir),
            "files_modified": files_modified,
        }

    except (ValueError, FileNotFoundError, OSError):
        # Rollback: remove the new version directory
        if new_dir.exists():
            shutil.rmtree(new_dir)
        raise


def main() -> None:
    """CLI entry point for the rule applicator."""
    parser = argparse.ArgumentParser(
        description="Apply approved consolidation proposals to rule files"
    )
    parser.add_argument(
        "--rules-dir",
        default="rules",
        help="Path to rules/ directory (default: rules)",
    )
    parser.add_argument(
        "--version",
        required=True,
        type=int,
        help="New version number (e.g., 1 for v1)",
    )
    parser.add_argument(
        "--proposal",
        required=True,
        help="Path to the approved proposal JSON file",
    )
    args = parser.parse_args()

    proposal = json.loads(Path(args.proposal).read_text())

    result = apply_rules(
        rules_base=Path(args.rules_dir),
        version=args.version,
        proposal=proposal,
    )

    print(json.dumps(result, indent=2))
    print(f"\nRules v{args.version} applied successfully.")
    print(f"Symlink updated: rules/current -> v{args.version}")


if __name__ == "__main__":
    main()
