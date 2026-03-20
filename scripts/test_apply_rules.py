"""Tests for rule applicator script.

Tests version directory creation, rule file copying, symlink update,
rollback on failure, 150-line cap, schema validation (no executable code blocks),
and change scope enforcement (20-line cap, 2-file cap). Written BEFORE implementation (TDD).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from scripts.apply_rules import (
    copy_rules_to_new_version,
    apply_proposal,
    update_symlink,
    validate_line_count,
    validate_no_executable_blocks,
    validate_change_scope,
    validate_file_count,
    apply_rules,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def rules_base(tmp_path: Path) -> Path:
    """Create a rules directory with v0 and a current symlink."""
    rules = tmp_path / "rules"
    rules.mkdir()
    v0 = rules / "v0"
    v0.mkdir()
    (v0 / "task-executor.md").write_text("# Task Executor\n\nLine 1\nLine 2\n")
    (v0 / "code-quality.md").write_text("# Code Quality\n\nLine 1\n")
    (v0 / "output-format.md").write_text("# Output Format\n\nLine 1\n")

    current = rules / "current"
    current.symlink_to("v0")
    return rules


@pytest.fixture
def simple_proposal() -> dict[str, Any]:
    """A valid proposal modifying 1 file with a small change."""
    return {
        "summary": {
            "rules_modified": ["task-executor.md"],
            "net_new_lines": {"task-executor.md": 3},
            "critiques_addressed": ["Critique 1 — Missing input validation"],
        },
        "changes": [
            {
                "file": "task-executor.md",
                "action": "ADD",
                "location": "after",
                "after_line": "Line 2",
                "new_text": "Line 3\nLine 4\nLine 5\n",
                "attribution": "Critique 1 — Missing input validation",
            }
        ],
    }


@pytest.fixture
def two_file_proposal() -> dict[str, Any]:
    """A valid proposal modifying 2 files."""
    return {
        "summary": {
            "rules_modified": ["task-executor.md", "code-quality.md"],
            "net_new_lines": {"task-executor.md": 2, "code-quality.md": 1},
            "critiques_addressed": ["Critique 1", "Critique 2"],
        },
        "changes": [
            {
                "file": "task-executor.md",
                "action": "ADD",
                "location": "after",
                "after_line": "Line 2",
                "new_text": "New line A\nNew line B\n",
                "attribution": "Critique 1",
            },
            {
                "file": "code-quality.md",
                "action": "ADD",
                "location": "after",
                "after_line": "Line 1",
                "new_text": "New line C\n",
                "attribution": "Critique 2",
            },
        ],
    }


# ---------------------------------------------------------------------------
# TestCopyRulesToNewVersion
# ---------------------------------------------------------------------------


class TestCopyRulesToNewVersion:
    """Tests for copy_rules_to_new_version()."""

    def test_creates_new_version_directory(self, rules_base: Path) -> None:
        """Should create rules/v1/ as a copy of the current rules."""
        new_dir = copy_rules_to_new_version(rules_base, version=1)
        assert new_dir.exists()
        assert new_dir.name == "v1"

    def test_copies_all_rule_files(self, rules_base: Path) -> None:
        """New version should contain all files from the source."""
        new_dir = copy_rules_to_new_version(rules_base, version=1)
        assert (new_dir / "task-executor.md").exists()
        assert (new_dir / "code-quality.md").exists()
        assert (new_dir / "output-format.md").exists()

    def test_content_matches_source(self, rules_base: Path) -> None:
        """Copied files should have identical content to the source."""
        new_dir = copy_rules_to_new_version(rules_base, version=1)
        original = (rules_base / "v0" / "task-executor.md").read_text()
        copied = (new_dir / "task-executor.md").read_text()
        assert copied == original

    def test_raises_if_version_exists(self, rules_base: Path) -> None:
        """Should raise if the target version directory already exists."""
        (rules_base / "v1").mkdir()
        with pytest.raises(FileExistsError):
            copy_rules_to_new_version(rules_base, version=1)


# ---------------------------------------------------------------------------
# TestUpdateSymlink
# ---------------------------------------------------------------------------


class TestUpdateSymlink:
    """Tests for update_symlink()."""

    def test_updates_symlink_target(self, rules_base: Path) -> None:
        """Should point current -> vN after update."""
        (rules_base / "v1").mkdir()
        update_symlink(rules_base, version=1)
        assert os.readlink(rules_base / "current") == "v1"

    def test_replaces_existing_symlink(self, rules_base: Path) -> None:
        """Should replace existing symlink, not fail."""
        (rules_base / "v1").mkdir()
        update_symlink(rules_base, version=1)
        # Now update again to v2
        (rules_base / "v2").mkdir()
        update_symlink(rules_base, version=2)
        assert os.readlink(rules_base / "current") == "v2"


# ---------------------------------------------------------------------------
# TestValidateLineCount
# ---------------------------------------------------------------------------


class TestValidateLineCount:
    """Tests for validate_line_count()."""

    def test_accepts_file_under_limit(self, tmp_path: Path) -> None:
        """Should not raise for files under 150 lines."""
        f = tmp_path / "small.md"
        f.write_text("\n".join(f"Line {i}" for i in range(100)))
        validate_line_count(f)  # should not raise

    def test_accepts_file_at_limit(self, tmp_path: Path) -> None:
        """Should not raise for files exactly at 150 lines."""
        f = tmp_path / "exact.md"
        f.write_text("\n".join(f"Line {i}" for i in range(150)))
        validate_line_count(f)  # should not raise

    def test_rejects_file_over_limit(self, tmp_path: Path) -> None:
        """Should raise ValueError for files exceeding 150 lines."""
        f = tmp_path / "big.md"
        f.write_text("\n".join(f"Line {i}" for i in range(200)))
        with pytest.raises(ValueError, match="150"):
            validate_line_count(f)


# ---------------------------------------------------------------------------
# TestValidateNoExecutableBlocks
# ---------------------------------------------------------------------------


class TestValidateNoExecutableBlocks:
    """Tests for validate_no_executable_blocks()."""

    def test_accepts_prose_content(self, tmp_path: Path) -> None:
        """Should not raise for markdown with no code blocks."""
        f = tmp_path / "prose.md"
        f.write_text("# Title\n\nJust prose here.\n")
        validate_no_executable_blocks(f)  # should not raise

    def test_accepts_pseudocode_blocks(self, tmp_path: Path) -> None:
        """Should allow fenced blocks without a language tag."""
        f = tmp_path / "pseudo.md"
        f.write_text("```\nsome pseudocode\n```\n")
        validate_no_executable_blocks(f)  # should not raise

    def test_rejects_python_blocks(self, tmp_path: Path) -> None:
        """Should raise for fenced python code blocks."""
        f = tmp_path / "bad.md"
        f.write_text("# Rules\n\n```python\nprint('hi')\n```\n")
        with pytest.raises(ValueError, match="executable"):
            validate_no_executable_blocks(f)

    def test_rejects_bash_blocks(self, tmp_path: Path) -> None:
        """Should raise for fenced bash code blocks."""
        f = tmp_path / "bad.md"
        f.write_text("# Rules\n\n```bash\nrm -rf /\n```\n")
        with pytest.raises(ValueError, match="executable"):
            validate_no_executable_blocks(f)

    def test_rejects_sh_blocks(self, tmp_path: Path) -> None:
        """Should raise for fenced sh code blocks."""
        f = tmp_path / "bad.md"
        f.write_text("# Rules\n\n```sh\necho hello\n```\n")
        with pytest.raises(ValueError, match="executable"):
            validate_no_executable_blocks(f)


# ---------------------------------------------------------------------------
# TestValidateChangeScope
# ---------------------------------------------------------------------------


class TestValidateChangeScope:
    """Tests for validate_change_scope()."""

    def test_accepts_within_line_cap(self) -> None:
        """Should not raise when net new lines are within the 20-line cap."""
        net_new = {"task-executor.md": 15}
        validate_change_scope(net_new)  # should not raise

    def test_accepts_at_line_cap(self) -> None:
        """Should not raise when exactly at 20 net new lines."""
        net_new = {"task-executor.md": 20}
        validate_change_scope(net_new)  # should not raise

    def test_rejects_over_line_cap(self) -> None:
        """Should raise when net new lines exceed 20 per file."""
        net_new = {"task-executor.md": 25}
        with pytest.raises(ValueError, match="20"):
            validate_change_scope(net_new)


# ---------------------------------------------------------------------------
# TestValidateFileCount
# ---------------------------------------------------------------------------


class TestValidateFileCount:
    """Tests for validate_file_count()."""

    def test_accepts_one_file(self) -> None:
        """Should not raise for 1 modified file."""
        validate_file_count(["task-executor.md"])  # should not raise

    def test_accepts_two_files(self) -> None:
        """Should not raise for 2 modified files."""
        validate_file_count(["task-executor.md", "code-quality.md"])  # should not raise

    def test_rejects_three_files(self) -> None:
        """Should raise when modifying all 3 rule files."""
        with pytest.raises(ValueError, match="2"):
            validate_file_count(
                ["task-executor.md", "code-quality.md", "output-format.md"]
            )


# ---------------------------------------------------------------------------
# TestApplyProposal
# ---------------------------------------------------------------------------


class TestApplyProposal:
    """Tests for apply_proposal()."""

    def test_adds_lines_to_file(self, rules_base: Path, simple_proposal: dict) -> None:
        """Should add new lines to the specified location in the file."""
        new_dir = copy_rules_to_new_version(rules_base, version=1)
        apply_proposal(new_dir, simple_proposal)

        content = (new_dir / "task-executor.md").read_text()
        assert "Line 3" in content
        assert "Line 4" in content
        assert "Line 5" in content

    def test_preserves_existing_content(
        self, rules_base: Path, simple_proposal: dict
    ) -> None:
        """Should not remove existing lines when adding new ones."""
        new_dir = copy_rules_to_new_version(rules_base, version=1)
        apply_proposal(new_dir, simple_proposal)

        content = (new_dir / "task-executor.md").read_text()
        assert "# Task Executor" in content
        assert "Line 1" in content
        assert "Line 2" in content

    def test_applies_to_multiple_files(
        self, rules_base: Path, two_file_proposal: dict
    ) -> None:
        """Should apply changes to all specified files."""
        new_dir = copy_rules_to_new_version(rules_base, version=1)
        apply_proposal(new_dir, two_file_proposal)

        te_content = (new_dir / "task-executor.md").read_text()
        cq_content = (new_dir / "code-quality.md").read_text()
        assert "New line A" in te_content
        assert "New line C" in cq_content


# ---------------------------------------------------------------------------
# TestApplyRules (integration)
# ---------------------------------------------------------------------------


class TestApplyRules:
    """Integration tests for apply_rules() — the main entry point."""

    def test_full_apply_flow(self, rules_base: Path, simple_proposal: dict) -> None:
        """Should copy, apply, validate, and update symlink."""
        result = apply_rules(rules_base, version=1, proposal=simple_proposal)

        assert result["version"] == 1
        assert result["success"] is True
        assert os.readlink(rules_base / "current") == "v1"

    def test_rejects_oversized_file(self, rules_base: Path) -> None:
        """Should reject and rollback if result exceeds 150 lines."""
        bloated_proposal = {
            "summary": {
                "rules_modified": ["task-executor.md"],
                "net_new_lines": {"task-executor.md": 20},
                "critiques_addressed": ["Critique 1"],
            },
            "changes": [
                {
                    "file": "task-executor.md",
                    "action": "ADD",
                    "location": "after",
                    "after_line": "Line 2",
                    "new_text": "\n".join(f"Extra {i}" for i in range(200)),
                    "attribution": "Critique 1",
                }
            ],
        }

        with pytest.raises(ValueError, match="150"):
            apply_rules(rules_base, version=1, proposal=bloated_proposal)

        # Symlink should still point to v0 (rollback)
        assert os.readlink(rules_base / "current") == "v0"

    def test_rejects_executable_blocks(self, rules_base: Path) -> None:
        """Should reject proposals that introduce executable code blocks."""
        bad_proposal = {
            "summary": {
                "rules_modified": ["task-executor.md"],
                "net_new_lines": {"task-executor.md": 5},
                "critiques_addressed": ["Critique 1"],
            },
            "changes": [
                {
                    "file": "task-executor.md",
                    "action": "ADD",
                    "location": "after",
                    "after_line": "Line 2",
                    "new_text": "```python\nprint('exploit')\n```\n",
                    "attribution": "Critique 1",
                }
            ],
        }

        with pytest.raises(ValueError, match="executable"):
            apply_rules(rules_base, version=1, proposal=bad_proposal)

        # Symlink should still point to v0 (rollback)
        assert os.readlink(rules_base / "current") == "v0"

    def test_rejects_three_file_modification(self, rules_base: Path) -> None:
        """Should reject proposals that modify all 3 rule files."""
        three_file = {
            "summary": {
                "rules_modified": [
                    "task-executor.md",
                    "code-quality.md",
                    "output-format.md",
                ],
                "net_new_lines": {
                    "task-executor.md": 1,
                    "code-quality.md": 1,
                    "output-format.md": 1,
                },
                "critiques_addressed": ["Critique 1", "Critique 2", "Critique 3"],
            },
            "changes": [
                {
                    "file": "task-executor.md",
                    "action": "ADD",
                    "location": "after",
                    "after_line": "Line 2",
                    "new_text": "X\n",
                    "attribution": "Critique 1",
                },
                {
                    "file": "code-quality.md",
                    "action": "ADD",
                    "location": "after",
                    "after_line": "Line 1",
                    "new_text": "Y\n",
                    "attribution": "Critique 2",
                },
                {
                    "file": "output-format.md",
                    "action": "ADD",
                    "location": "after",
                    "after_line": "Line 1",
                    "new_text": "Z\n",
                    "attribution": "Critique 3",
                },
            ],
        }

        with pytest.raises(ValueError, match="2"):
            apply_rules(rules_base, version=1, proposal=three_file)

    def test_rollback_on_validation_failure(self, rules_base: Path) -> None:
        """On failure, the new version directory should be cleaned up."""
        bad_proposal = {
            "summary": {
                "rules_modified": ["task-executor.md"],
                "net_new_lines": {"task-executor.md": 200},
                "critiques_addressed": ["Critique 1"],
            },
            "changes": [
                {
                    "file": "task-executor.md",
                    "action": "ADD",
                    "location": "after",
                    "after_line": "Line 2",
                    "new_text": "\n".join(f"L{i}" for i in range(200)),
                    "attribution": "Critique 1",
                }
            ],
        }

        with pytest.raises(ValueError):
            apply_rules(rules_base, version=1, proposal=bad_proposal)

        # v1 should have been cleaned up
        assert not (rules_base / "v1").exists()
