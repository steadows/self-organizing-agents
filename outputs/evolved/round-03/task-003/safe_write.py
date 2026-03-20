"""Atomic file write utility using a temporary file and os.replace."""

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
    then renames it atomically using ``os.replace``. This guarantees the
    target is never left in a partially-written state. Parent directories
    are created automatically if they do not exist.

    If the target file already exists, its permissions are preserved after
    the rename. If the target does not exist, default permissions are used.

    Parameters
    ----------
    path:
        Destination file path (``str`` or ``pathlib.Path``).
    content:
        Data to write. Must be ``str`` or ``bytes``.
    mode:
        File open mode passed through for reference; actual mode is derived
        from the type of ``content`` (text for ``str``, binary for ``bytes``).
    encoding:
        Text encoding used when ``content`` is ``str``. Ignored for ``bytes``.

    Raises
    ------
    TypeError
        If ``content`` is neither ``str`` nor ``bytes``.
    OSError
        If a filesystem error occurs (propagated after temp-file cleanup).

    Examples
    --------
    >>> import tempfile, os
    >>> with tempfile.TemporaryDirectory() as d:
    ...     safe_write(f"{d}/hello.txt", "hello world")
    ...     open(f"{d}/hello.txt").read()
    'hello world'
    """
    if not isinstance(content, (str, bytes)):
        raise TypeError(
            f"content must be str or bytes, got {type(content).__name__!r}"
        )

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Capture existing permissions before we replace the file.
    existing_mode: int | None = None
    if target.exists():
        existing_mode = target.stat().st_mode

    tmp_path: str | None = None
    try:
        if isinstance(content, bytes):
            tmp_fd, tmp_path = tempfile.mkstemp(dir=target.parent)
            with os.fdopen(tmp_fd, "wb") as fh:
                fh.write(content)
        else:
            tmp_fd, tmp_path = tempfile.mkstemp(dir=target.parent)
            with os.fdopen(tmp_fd, "w", encoding=encoding) as fh:
                fh.write(content)

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
