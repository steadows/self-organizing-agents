"""Acceptance tests for task-003: safe_write()

Tests the contract:
  safe_write(
      path: str | Path,
      content: str | bytes,
      *,
      mode: str = "w",
      encoding: str = "utf-8",
  ) -> None

Atomically writes content to a file, creating parent directories as needed.
The file is either fully written or not present (no partial writes).

These tests are FROZEN ground truth. Implementations must pass all of them.
"""

import os
import sys
from pathlib import Path

import pytest

# Allow importing from the output directory passed via environment variable
# or default to the current directory
output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(__file__))
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

from safe_write import safe_write


# ── Happy path ──────────────────────────────────────────────────────────────

def test_safe_write_text_file(tmp_path: Path) -> None:
    """Write a text file and read it back."""
    target = tmp_path / "hello.txt"
    safe_write(target, "hello world")
    assert target.read_text(encoding="utf-8") == "hello world"


def test_safe_write_str_path(tmp_path: Path) -> None:
    """Accept a plain str path."""
    target = str(tmp_path / "str_path.txt")
    safe_write(target, "content")
    assert Path(target).read_text(encoding="utf-8") == "content"


def test_safe_write_pathlib_path(tmp_path: Path) -> None:
    """Accept a pathlib.Path."""
    target = tmp_path / "pathlib_path.txt"
    safe_write(target, "content")
    assert target.read_text(encoding="utf-8") == "content"


def test_safe_write_returns_none(tmp_path: Path) -> None:
    """Return value is None."""
    result = safe_write(tmp_path / "ret.txt", "data")
    assert result is None


# ── Binary mode ─────────────────────────────────────────────────────────────

def test_safe_write_binary(tmp_path: Path) -> None:
    """Write bytes in binary mode."""
    target = tmp_path / "binary.bin"
    data = b"\x00\x01\x02\xff"
    safe_write(target, data, mode="wb")
    assert target.read_bytes() == data


def test_safe_write_binary_roundtrip(tmp_path: Path) -> None:
    """Binary content survives a roundtrip."""
    target = tmp_path / "roundtrip.bin"
    content = bytes(range(256))
    safe_write(target, content, mode="wb")
    assert target.read_bytes() == content


# ── Atomic behaviour ───────────────────────────────────────────────────────

def test_safe_write_file_exists_after_write(tmp_path: Path) -> None:
    """After a successful write, the file exists with correct content."""
    target = tmp_path / "atomic.txt"
    safe_write(target, "atomic content")
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "atomic content"


# ── Parent directory creation ──────────────────────────────────────────────

def test_safe_write_creates_parent_dirs(tmp_path: Path) -> None:
    """Non-existent parent directories are created automatically."""
    target = tmp_path / "a" / "b" / "c" / "deep.txt"
    safe_write(target, "deep content")
    assert target.read_text(encoding="utf-8") == "deep content"


def test_safe_write_existing_parent_dirs(tmp_path: Path) -> None:
    """Works when parent directories already exist."""
    subdir = tmp_path / "existing"
    subdir.mkdir()
    target = subdir / "file.txt"
    safe_write(target, "content")
    assert target.read_text(encoding="utf-8") == "content"


# ── Overwrite ──────────────────────────────────────────────────────────────

def test_safe_write_overwrite(tmp_path: Path) -> None:
    """A second write overwrites the first."""
    target = tmp_path / "overwrite.txt"
    safe_write(target, "first")
    safe_write(target, "second")
    assert target.read_text(encoding="utf-8") == "second"


def test_safe_write_overwrite_shorter_content(tmp_path: Path) -> None:
    """Overwriting with shorter content does not leave leftovers."""
    target = tmp_path / "shrink.txt"
    safe_write(target, "long content here")
    safe_write(target, "short")
    assert target.read_text(encoding="utf-8") == "short"


# ── Empty content ──────────────────────────────────────────────────────────

def test_safe_write_empty_string(tmp_path: Path) -> None:
    """Writing an empty string creates an empty file."""
    target = tmp_path / "empty.txt"
    safe_write(target, "")
    assert target.exists()
    assert target.read_text(encoding="utf-8") == ""


def test_safe_write_empty_bytes(tmp_path: Path) -> None:
    """Writing empty bytes creates an empty file."""
    target = tmp_path / "empty.bin"
    safe_write(target, b"", mode="wb")
    assert target.exists()
    assert target.read_bytes() == b""


# ── Encoding ───────────────────────────────────────────────────────────────

def test_safe_write_utf8_content(tmp_path: Path) -> None:
    """UTF-8 encoded content roundtrips correctly."""
    target = tmp_path / "utf8.txt"
    content = "café résumé naïve"
    safe_write(target, content, encoding="utf-8")
    assert target.read_text(encoding="utf-8") == content


def test_safe_write_custom_encoding(tmp_path: Path) -> None:
    """A non-default encoding is respected."""
    target = tmp_path / "latin1.txt"
    content = "café"
    safe_write(target, content, encoding="latin-1")
    assert target.read_bytes() == content.encode("latin-1")


# ── Error handling ─────────────────────────────────────────────────────────

def test_safe_write_int_content_raises_type_error(tmp_path: Path) -> None:
    """Passing a non-str/bytes content raises TypeError."""
    target = tmp_path / "bad.txt"
    with pytest.raises(TypeError):
        safe_write(target, 12345)  # type: ignore[arg-type]


def test_safe_write_none_content_raises_type_error(tmp_path: Path) -> None:
    """Passing None as content raises TypeError."""
    target = tmp_path / "bad.txt"
    with pytest.raises(TypeError):
        safe_write(target, None)  # type: ignore[arg-type]
