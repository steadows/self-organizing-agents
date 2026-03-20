"""Tests for the safe_write utility."""

import os
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from safe_write import safe_write


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_writes_text_content(tmp_path: Path) -> None:
    """Basic text write creates the file with correct content."""
    target = tmp_path / "output.txt"
    safe_write(target, "hello world")
    assert target.read_text() == "hello world"


def test_writes_bytes_content(tmp_path: Path) -> None:
    """Basic binary write creates the file with correct content."""
    target = tmp_path / "output.bin"
    safe_write(target, b"\x89PNG\r\n\x1a\n")
    assert target.read_bytes() == b"\x89PNG\r\n\x1a\n"


def test_accepts_string_path(tmp_path: Path) -> None:
    """Path given as a plain str is accepted."""
    target = tmp_path / "str_path.txt"
    safe_write(str(target), "via string path")
    assert target.read_text() == "via string path"


def test_creates_parent_directories(tmp_path: Path) -> None:
    """Non-existent parent directories are created automatically."""
    target = tmp_path / "a" / "b" / "c" / "file.txt"
    safe_write(target, "nested")
    assert target.read_text() == "nested"


def test_overwrites_existing_file(tmp_path: Path) -> None:
    """An existing file is atomically replaced."""
    target = tmp_path / "data.txt"
    target.write_text("original")
    safe_write(target, "updated")
    assert target.read_text() == "updated"


def test_empty_string_writes_empty_file(tmp_path: Path) -> None:
    """Empty string content produces an empty file (valid operation)."""
    target = tmp_path / "empty.txt"
    safe_write(target, "")
    assert target.read_text() == ""


def test_empty_bytes_writes_empty_file(tmp_path: Path) -> None:
    """Empty bytes content produces an empty file (valid operation)."""
    target = tmp_path / "empty.bin"
    safe_write(target, b"")
    assert target.read_bytes() == b""


def test_encoding_parameter_is_used(tmp_path: Path) -> None:
    """Custom encoding is respected for text content."""
    target = tmp_path / "latin.txt"
    safe_write(target, "caf\u00e9", encoding="latin-1")
    assert target.read_text(encoding="latin-1") == "caf\u00e9"


# ---------------------------------------------------------------------------
# Permission preservation
# ---------------------------------------------------------------------------


def test_preserves_permissions_of_existing_file(tmp_path: Path) -> None:
    """Existing file permissions survive an atomic overwrite."""
    target = tmp_path / "perms.txt"
    target.write_text("original")
    os.chmod(target, 0o600)

    safe_write(target, "updated")

    actual_mode = stat.S_IMODE(target.stat().st_mode)
    assert actual_mode == 0o600


# ---------------------------------------------------------------------------
# Error / edge-case tests
# ---------------------------------------------------------------------------


def test_raises_type_error_for_int_content(tmp_path: Path) -> None:
    """Non-str/bytes content raises TypeError."""
    with pytest.raises(TypeError, match="content must be str or bytes"):
        safe_write(tmp_path / "bad.txt", 42)  # type: ignore[arg-type]


def test_raises_type_error_for_list_content(tmp_path: Path) -> None:
    """List content raises TypeError."""
    with pytest.raises(TypeError, match="content must be str or bytes"):
        safe_write(tmp_path / "bad.txt", ["a", "b"])  # type: ignore[arg-type]


def test_temp_file_cleaned_up_on_write_failure(tmp_path: Path) -> None:
    """Temporary file is removed when writing raises an OSError."""
    target = tmp_path / "output.txt"

    # Intercept fdopen so the write raises after mkstemp creates the temp file.
    original_fdopen = os.fdopen

    def failing_fdopen(fd: int, *args, **kwargs):  # noqa: ANN001
        """Raise immediately, leaving the temp file on disk momentarily."""
        os.close(fd)
        raise OSError("simulated write failure")

    with patch("os.fdopen", side_effect=failing_fdopen):
        with pytest.raises(OSError, match="simulated write failure"):
            safe_write(target, "content")

    # After the exception the temp file should have been cleaned up.
    remaining = list(tmp_path.iterdir())
    assert remaining == [], f"Unexpected files left behind: {remaining}"


def test_os_replace_failure_cleans_up_temp_file(tmp_path: Path) -> None:
    """Temporary file is removed when os.replace raises."""
    target = tmp_path / "output.txt"

    with patch("os.replace", side_effect=OSError("simulated replace failure")):
        with pytest.raises(OSError, match="simulated replace failure"):
            safe_write(target, "content")

    remaining = list(tmp_path.iterdir())
    assert remaining == [], f"Unexpected files left behind: {remaining}"


def test_target_not_written_on_failure(tmp_path: Path) -> None:
    """Target file is not created when the write fails mid-way."""
    target = tmp_path / "never.txt"

    with patch("os.replace", side_effect=OSError("boom")):
        with pytest.raises(OSError):
            safe_write(target, "data")

    assert not target.exists()
