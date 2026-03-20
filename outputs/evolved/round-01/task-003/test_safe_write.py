"""Tests for the safe_write utility."""

import os
import stat
import tempfile
from pathlib import Path

import pytest

from safe_write import safe_write


def test_write_text_file(tmp_path: Path) -> None:
    """Writing a text string creates the file with expected content."""
    target = tmp_path / "output.txt"
    safe_write(target, "hello world")
    assert target.read_text(encoding="utf-8") == "hello world"


def test_write_bytes_file(tmp_path: Path) -> None:
    """Writing bytes creates a binary file with expected content."""
    target = tmp_path / "data.bin"
    safe_write(target, b"\x89PNG\r\n")
    assert target.read_bytes() == b"\x89PNG\r\n"


def test_accepts_str_path(tmp_path: Path) -> None:
    """Path can be supplied as a plain string."""
    target = str(tmp_path / "str_path.txt")
    safe_write(target, "via string path")
    assert Path(target).read_text(encoding="utf-8") == "via string path"


def test_creates_parent_directories(tmp_path: Path) -> None:
    """Parent directories are created automatically when missing."""
    target = tmp_path / "a" / "b" / "c" / "file.txt"
    safe_write(target, "nested")
    assert target.read_text(encoding="utf-8") == "nested"


def test_overwrites_existing_file(tmp_path: Path) -> None:
    """An existing file is atomically replaced."""
    target = tmp_path / "file.txt"
    target.write_text("original", encoding="utf-8")
    safe_write(target, "updated")
    assert target.read_text(encoding="utf-8") == "updated"


def test_empty_string_content(tmp_path: Path) -> None:
    """Empty string writes a valid empty file."""
    target = tmp_path / "empty.txt"
    safe_write(target, "")
    assert target.read_text(encoding="utf-8") == ""


def test_empty_bytes_content(tmp_path: Path) -> None:
    """Empty bytes writes a valid empty file."""
    target = tmp_path / "empty.bin"
    safe_write(target, b"")
    assert target.read_bytes() == b""


def test_raises_type_error_for_invalid_content(tmp_path: Path) -> None:
    """Passing a non-str/bytes value raises TypeError."""
    target = tmp_path / "bad.txt"
    with pytest.raises(TypeError, match="str or bytes"):
        safe_write(target, 42)  # type: ignore[arg-type]


def test_raises_type_error_for_list_content(tmp_path: Path) -> None:
    """Passing a list raises TypeError."""
    target = tmp_path / "bad.txt"
    with pytest.raises(TypeError):
        safe_write(target, ["not", "valid"])  # type: ignore[arg-type]


def test_custom_encoding(tmp_path: Path) -> None:
    """Text content is written with the specified encoding."""
    target = tmp_path / "latin.txt"
    content = "caf\u00e9"
    safe_write(target, content, encoding="utf-8")
    assert target.read_text(encoding="utf-8") == content


def test_preserves_permissions_on_overwrite(tmp_path: Path) -> None:
    """Existing file permissions are preserved after an atomic replace."""
    target = tmp_path / "file.txt"
    target.write_text("original", encoding="utf-8")
    # Set a specific permission mask (read/write for owner only).
    os.chmod(target, 0o600)
    original_mode = stat.S_IMODE(target.stat().st_mode)

    safe_write(target, "updated")

    new_mode = stat.S_IMODE(target.stat().st_mode)
    assert new_mode == original_mode


def test_no_temp_file_left_on_success(tmp_path: Path) -> None:
    """No stray temporary files remain in the target directory after success."""
    target = tmp_path / "file.txt"
    safe_write(target, "content")
    files = list(tmp_path.iterdir())
    assert files == [target]


def test_binary_encoding_ignored(tmp_path: Path) -> None:
    """Encoding parameter is ignored when content is bytes."""
    target = tmp_path / "binary.bin"
    data = b"\xff\xfe"
    # Passing encoding should not raise even for binary content.
    safe_write(target, data, encoding="ascii")
    assert target.read_bytes() == data
