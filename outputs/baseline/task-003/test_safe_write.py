"""Tests for safe_write atomic file writing utility."""

import os
import stat
from pathlib import Path

import pytest

from safe_write import safe_write


def test_write_text_file(tmp_path: Path) -> None:
    """Write a simple text string and verify contents."""
    target = tmp_path / "data.txt"
    safe_write(target, "hello world")
    assert target.read_text() == "hello world"


def test_write_bytes_file(tmp_path: Path) -> None:
    """Write binary content and verify contents."""
    target = tmp_path / "image.bin"
    payload = b"\x89PNG\r\n"
    safe_write(target, payload)
    assert target.read_bytes() == payload


def test_overwrites_existing_file(tmp_path: Path) -> None:
    """Atomically replace an existing file."""
    target = tmp_path / "data.txt"
    safe_write(target, "original")
    safe_write(target, "updated")
    assert target.read_text() == "updated"


def test_creates_nested_directories(tmp_path: Path) -> None:
    """Parent directories are created if they don't exist."""
    target = tmp_path / "a" / "b" / "c" / "file.txt"
    safe_write(target, "content")
    assert target.read_text() == "content"


def test_empty_string_content(tmp_path: Path) -> None:
    """Empty string writes an empty file."""
    target = tmp_path / "empty.txt"
    safe_write(target, "")
    assert target.read_text() == ""
    assert target.stat().st_size == 0


def test_empty_bytes_content(tmp_path: Path) -> None:
    """Empty bytes writes an empty file."""
    target = tmp_path / "empty.bin"
    safe_write(target, b"")
    assert target.read_bytes() == b""
    assert target.stat().st_size == 0


def test_raises_type_error_for_int(tmp_path: Path) -> None:
    """Non-str/bytes content raises TypeError."""
    with pytest.raises(TypeError, match="content must be str or bytes"):
        safe_write(tmp_path / "bad.txt", 42)  # type: ignore[arg-type]


def test_raises_type_error_for_list(tmp_path: Path) -> None:
    """Non-str/bytes content raises TypeError."""
    with pytest.raises(TypeError, match="content must be str or bytes"):
        safe_write(tmp_path / "bad.txt", ["a", "b"])  # type: ignore[arg-type]


def test_accepts_str_path(tmp_path: Path) -> None:
    """Path provided as a plain string works."""
    target = str(tmp_path / "str_path.txt")
    safe_write(target, "works")
    assert Path(target).read_text() == "works"


def test_preserves_existing_permissions(tmp_path: Path) -> None:
    """If target exists, its permissions are preserved after overwrite."""
    target = tmp_path / "perm.txt"
    target.write_text("original")
    os.chmod(target, 0o644)

    safe_write(target, "updated")

    current_mode = stat.S_IMODE(target.stat().st_mode)
    assert current_mode == 0o644


def test_default_permissions_for_new_file(tmp_path: Path) -> None:
    """New file gets default permissions (not an error)."""
    target = tmp_path / "new.txt"
    safe_write(target, "hello")
    assert target.exists()


def test_encoding_parameter(tmp_path: Path) -> None:
    """Custom encoding is respected for text content."""
    target = tmp_path / "latin.txt"
    safe_write(target, "caf\u00e9", encoding="latin-1")
    raw = target.read_bytes()
    assert raw == "caf\u00e9".encode("latin-1")


def test_no_temp_file_left_on_success(tmp_path: Path) -> None:
    """After a successful write only the target file exists in the directory."""
    target = tmp_path / "clean.txt"
    safe_write(target, "data")
    files = list(tmp_path.iterdir())
    assert files == [target]
