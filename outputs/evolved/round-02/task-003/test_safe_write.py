"""Tests for the safe_write atomic file-write utility."""

import os
import stat
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from safe_write import safe_write


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_writes_text_content(tmp_path: Path) -> None:
    target = tmp_path / "hello.txt"
    safe_write(target, "hello world")
    assert target.read_text(encoding="utf-8") == "hello world"


def test_writes_bytes_content(tmp_path: Path) -> None:
    target = tmp_path / "data.bin"
    safe_write(target, b"\x89PNG\r\n")
    assert target.read_bytes() == b"\x89PNG\r\n"


def test_accepts_str_path(tmp_path: Path) -> None:
    target = str(tmp_path / "str_path.txt")
    safe_write(target, "via string path")
    assert Path(target).read_text() == "via string path"


def test_creates_parent_directories(tmp_path: Path) -> None:
    target = tmp_path / "a" / "b" / "c" / "file.txt"
    safe_write(target, "nested")
    assert target.read_text() == "nested"


def test_overwrites_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("old content")
    safe_write(target, "new content")
    assert target.read_text() == "new content"


def test_writes_empty_string(tmp_path: Path) -> None:
    target = tmp_path / "empty.txt"
    safe_write(target, "")
    assert target.read_text() == ""
    assert target.stat().st_size == 0


def test_writes_empty_bytes(tmp_path: Path) -> None:
    target = tmp_path / "empty.bin"
    safe_write(target, b"")
    assert target.read_bytes() == b""
    assert target.stat().st_size == 0


def test_respects_encoding_parameter(tmp_path: Path) -> None:
    target = tmp_path / "latin.txt"
    safe_write(target, "caf\u00e9", encoding="latin-1")
    assert target.read_text(encoding="latin-1") == "café"


def test_preserves_permissions_on_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "perms.txt"
    target.write_text("original")
    # Set a non-default permission (read-only for owner).
    os.chmod(target, 0o644)
    original_mode = stat.S_IMODE(target.stat().st_mode)

    # Make writable again so safe_write can replace it.
    os.chmod(target, 0o644)
    safe_write(target, "updated")

    new_mode = stat.S_IMODE(target.stat().st_mode)
    assert new_mode == original_mode


def test_no_leftover_temp_files_on_success(tmp_path: Path) -> None:
    target = tmp_path / "clean.txt"
    safe_write(target, "content")
    files = list(tmp_path.iterdir())
    assert files == [target]


# ---------------------------------------------------------------------------
# TypeError tests
# ---------------------------------------------------------------------------


def test_raises_type_error_for_int(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="str or bytes"):
        safe_write(tmp_path / "bad.txt", 42)  # type: ignore[arg-type]


def test_raises_type_error_for_list(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="str or bytes"):
        safe_write(tmp_path / "bad.txt", ["a", "b"])  # type: ignore[arg-type]


def test_raises_type_error_for_none(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="str or bytes"):
        safe_write(tmp_path / "bad.txt", None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Failure / error-path tests
# ---------------------------------------------------------------------------


def test_cleans_up_temp_file_on_write_failure(tmp_path: Path) -> None:
    """If writing to the temp file raises, the temp file is deleted."""
    target = tmp_path / "fail.txt"

    with patch("tempfile.NamedTemporaryFile") as mock_ntf:
        mock_file = mock_ntf.return_value.__enter__.return_value
        mock_file.name = str(tmp_path / "fake_tmp")
        # Simulate a disk-full error during write.
        mock_file.write.side_effect = OSError("no space left on device")

        # Create the fake temp path so unlink has something to act on.
        Path(mock_file.name).touch()

        with pytest.raises(OSError, match="no space left"):
            safe_write(target, "data")

        # Temp file must have been removed.
        assert not Path(mock_file.name).exists()


def test_propagates_os_replace_error(tmp_path: Path) -> None:
    """If os.replace fails, the OSError propagates and temp file is cleaned up."""
    target = tmp_path / "replace_fail.txt"

    with patch("os.replace", side_effect=OSError("rename failed")):
        with pytest.raises(OSError, match="rename failed"):
            safe_write(target, "data")

    # No temp files should remain in the directory.
    remaining = [f for f in tmp_path.iterdir() if f != target]
    assert remaining == []


def test_propagates_mkdir_error(tmp_path: Path) -> None:
    """If mkdir raises, the error propagates before any temp file is created."""
    target = tmp_path / "sub" / "file.txt"

    with patch("pathlib.Path.mkdir", side_effect=PermissionError("no permission")):
        with pytest.raises(PermissionError, match="no permission"):
            safe_write(target, "data")
