# Task 003: safe_write

## Function Signature

```python
from pathlib import Path

def safe_write(
    path: str | Path,
    content: str | bytes,
    *,
    mode: str = "w",
    encoding: str = "utf-8",
) -> None:
```

## Description

Write content to a file atomically by first writing to a temporary file in the same directory, then renaming it to the target path. This ensures that the target file is never left in a partially-written state. Parent directories are created automatically if they do not exist.

## Requirements

- Accept `path` as either `str` or `pathlib.Path`; normalize to `Path` internally.
- Create parent directories (`parents=True, exist_ok=True`) if they do not already exist.
- Write content to a temporary file in the **same directory** as the target (use `tempfile.NamedTemporaryFile` with `dir=path.parent`, `delete=False`).
- After writing completes successfully, call `os.replace()` (not `os.rename()`) to atomically move the temp file to the target path. `os.replace` is atomic on POSIX and overwrites existing files.
- If writing or renaming fails, delete the temporary file in a `finally` block (best-effort cleanup).
- When `content` is `str`: open temp file in text mode (`"w"`) with the specified `encoding`.
- When `content` is `bytes`: open temp file in binary mode (`"wb"`); ignore the `encoding` parameter.
- Preserve the file's existing permissions if the target already exists (read permissions from target before writing, apply with `os.chmod` after rename). If the target does not exist, use default permissions.
- Raise `TypeError` if `content` is neither `str` nor `bytes`.
- No external dependencies; use only `pathlib`, `tempfile`, `os`.

## Edge Cases

- Empty string content `""` writes an empty file (valid operation).
- Empty bytes content `b""` writes an empty file (valid operation).
- Path with non-existent parent directories: directories are created, file is written.
- If the target file already exists, it is atomically replaced.
- Permission error creating the temp file or parent directories: let the `OSError` / `PermissionError` propagate after cleaning up the temp file.
- Content is `int` or other non-str/bytes type: raise `TypeError` with a descriptive message.

## Examples

```python
# Write a text file
safe_write("/tmp/output/data.txt", "hello world")

# Write binary content
safe_write("/tmp/output/image.bin", b"\x89PNG\r\n")

# Overwrites existing file atomically
safe_write("/tmp/output/data.txt", "updated content")

# Creates nested directories
safe_write("/tmp/deeply/nested/dir/file.txt", "content")

# Empty content is valid
safe_write("/tmp/output/empty.txt", "")

# TypeError for invalid content
safe_write("/tmp/bad.txt", 42)  # raises TypeError
```

## Scope Boundary

- POSIX only. No Windows-specific handling (no `MoveFileEx`, no handling of cross-volume renames).
- NO multi-file atomic transactions or rollback.
- NO file locking (`fcntl.flock`, etc.).
- NO `fsync` / `fdatasync` (durability on power loss is not guaranteed).
- NO support for writing to file-like objects or streams.
