"""Atomic file writing utility.

Writes content to a file atomically by first writing to a temporary file
in the same directory, then renaming it to the target path. This ensures
the target file is never left in a partially-written state.
"""

import os
import tempfile
from pathlib import Path


def safe_write(
    path: str | Path,
    content: str | bytes,
    *,
    mode: str = "w",
    encoding: str = "utf-8",
) -> None:
    """Write content to a file atomically using a temp-file-then-rename strategy.

    Parent directories are created automatically if they do not exist.
    If the target file already exists, its permissions are preserved.

    Args:
        path: Destination file path (str or Path).
        content: The data to write. Must be str or bytes.
        mode: File open mode (used only for informational context; actual mode
              is determined by the type of content).
        encoding: Text encoding when content is str. Ignored for bytes.

    Raises:
        TypeError: If content is neither str nor bytes.
        OSError: If directory creation, writing, or renaming fails.
    """
    if not isinstance(content, (str, bytes)):
        raise TypeError(
            f"content must be str or bytes, got {type(content).__name__}"
        )

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Capture existing permissions before we overwrite
    existing_permissions: int | None = None
    if path.exists():
        existing_permissions = path.stat().st_mode

    tmp_path: str | None = None
    try:
        if isinstance(content, bytes):
            tmp_fd = tempfile.NamedTemporaryFile(
                dir=path.parent, delete=False, mode="wb"
            )
        else:
            tmp_fd = tempfile.NamedTemporaryFile(
                dir=path.parent, delete=False, mode="w", encoding=encoding
            )

        tmp_path = tmp_fd.name
        with tmp_fd:
            tmp_fd.write(content)

        os.replace(tmp_path, path)

        if existing_permissions is not None:
            os.chmod(path, existing_permissions)

    except BaseException:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise
