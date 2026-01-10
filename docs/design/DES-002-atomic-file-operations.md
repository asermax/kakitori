# DES-002: Atomic File Operations with Temp Files

**Scope**: Project-wide
**Date**: 2026-01-01
**Last Updated**: 2026-01-01

## Pattern

When writing files that must be complete or not exist at all, write to a temporary location first, then move to the final destination on success.

## Rationale

Partial or corrupted files at the destination confuse users and tools. By writing to `/tmp/` first:
- Interrupted operations leave no file at destination
- Failed operations don't overwrite valid existing files
- Users see only complete, valid files

## Examples

### Do This

```python
from pathlib import Path
import shutil

def record_to_file(output_path: Path) -> bool:
    temp_path = Path("/tmp") / f"{output_path.stem}_temp{output_path.suffix}"

    try:
        # Write to temp location
        write_data_to(temp_path)

        # Atomic move on success
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(temp_path), str(output_path))
        return True

    except Exception:
        # Clean up temp file on failure
        temp_path.unlink(missing_ok=True)
        raise
```

**Why**: If writing fails, no file exists at `output_path`. Users never see partial files.

### Don't Do This

```python
def record_to_file(output_path: Path) -> bool:
    with open(output_path, "wb") as f:
        # Write directly to destination
        write_data_to(f)
    return True
```

**Why**: If writing fails mid-stream, a partial file remains at `output_path`.

## Exceptions

- Small files that write quickly (config files, metadata)
- Files where partial content is acceptable (logs, debug output)
- When `/tmp` space is constrained and destination has more space

---

## Evolution

### Version 1 (2026-01-01)

Initial pattern established from RECORD-001 retrofit.

---

## Related

- Promoted from: [../feature-designs/RECORD-001.md](../feature-designs/RECORD-001.md)
- Applied in: `src/kakitori/record/recorder.py`
