"""Utility for atomically writing content to a file."""

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
    """Write content to a file atomically via a temporary file and rename.

    Writes content to a temporary file in the same directory as the target,
    then renames it atomically to the target path. This ensures the target
    is never left in a partially-written state. Parent directories are
    created automatically if they do not exist.

    Args:
        path: Destination file path (str or Path).
        content: Content to write; must be str or bytes.
        mode: Unused parameter kept for API compatibility (write mode is
              inferred from content type).
        encoding: Text encoding used when content is str. Ignored for bytes.

    Raises:
        TypeError: If content is neither str nor bytes.
        OSError: If the temporary file or parent directories cannot be created,
                 or if the atomic rename fails.
    """
    if not isinstance(content, (str, bytes)):
        raise TypeError(
            f"content must be str or bytes, got {type(content).__name__!r}"
        )

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Capture existing permissions before writing, if target exists.
    existing_permissions: int | None = None
    if target.exists():
        existing_permissions = target.stat().st_mode

    tmp_path: str | None = None
    try:
        if isinstance(content, bytes):
            with tempfile.NamedTemporaryFile(
                dir=target.parent, delete=False, mode="wb"
            ) as tmp_file:
                tmp_path = tmp_file.name
                tmp_file.write(content)
        else:
            with tempfile.NamedTemporaryFile(
                dir=target.parent, delete=False, mode="w", encoding=encoding
            ) as tmp_file:
                tmp_path = tmp_file.name
                tmp_file.write(content)

        os.replace(tmp_path, target)
        tmp_path = None  # Rename succeeded; no cleanup needed.

        if existing_permissions is not None:
            os.chmod(target, existing_permissions)

    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
