"""Atomic file write utility using a write-then-rename pattern."""

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
    then renames it to the target path using ``os.replace``. This guarantees
    the target is never left in a partially-written state. Parent directories
    are created automatically when they do not exist.

    If the target file already exists, its permissions are preserved after the
    atomic replace. If it does not exist, default permissions apply.

    Parameters
    ----------
    path:
        Destination file path (``str`` or ``pathlib.Path``).
    content:
        Data to write. Must be ``str`` or ``bytes``.
    mode:
        Unused for dispatch (write mode is derived from content type), kept
        for API compatibility.
    encoding:
        Text encoding used when ``content`` is ``str``. Ignored for ``bytes``.

    Raises
    ------
    TypeError
        If ``content`` is neither ``str`` nor ``bytes``.
    OSError
        If the parent directory cannot be created or the temp file cannot be
        written or renamed. The temporary file is cleaned up before the
        exception propagates.

    Examples
    --------
    >>> import tempfile, os
    >>> with tempfile.TemporaryDirectory() as d:
    ...     safe_write(d + "/hello.txt", "hello world")
    ...     open(d + "/hello.txt").read()
    'hello world'
    """
    if not isinstance(content, (str, bytes)):
        raise TypeError(
            f"content must be str or bytes, got {type(content).__name__!r}"
        )

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Capture existing permissions before we overwrite.
    existing_mode: int | None = None
    if target.exists():
        existing_mode = target.stat().st_mode

    tmp_path: str | None = None
    try:
        if isinstance(content, bytes):
            with tempfile.NamedTemporaryFile(
                dir=target.parent, delete=False, mode="wb"
            ) as tmp:
                tmp_path = tmp.name
                tmp.write(content)
        else:
            with tempfile.NamedTemporaryFile(
                dir=target.parent, delete=False, mode="w", encoding=encoding
            ) as tmp:
                tmp_path = tmp.name
                tmp.write(content)

        os.replace(tmp_path, target)
        tmp_path = None  # rename succeeded; no cleanup needed

        if existing_mode is not None:
            os.chmod(target, existing_mode)

    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
