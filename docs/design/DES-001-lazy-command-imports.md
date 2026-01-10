# DES-001: Lazy Command Imports

**Scope**: Project-wide
**Date**: 2026-01-01
**Last Updated**: 2026-01-01

## Pattern

Import command modules inside their handler functions rather than at module level. This defers loading of command-specific dependencies until the command is actually invoked.

## Rationale

Different commands have different dependencies:
- `record`: PulseAudio bindings, ffmpeg subprocess
- `process`: Gemini API client, pydantic models

Lazy imports provide:
- Faster startup when using only one command
- Partial functionality if some dependencies are missing
- Cleaner separation of command concerns

## Examples

### Do This

```python
def _run_record_command(args) -> None:
    """Execute the record subcommand."""
    from kakitori.record import run_record  # Lazy import

    config = _load_config()
    # ... use run_record
```

**Why**: The `kakitori.record` module and its dependencies are only loaded when the user runs `kakitori record`.

### Don't Do This

```python
from kakitori.record import run_record  # Eager import at module level
from kakitori.process import run_process

def _run_record_command(args) -> None:
    # ... use run_record
```

**Why**: This loads both command modules and all their dependencies at startup, even if only one command is used.

## Exceptions

- Shared utilities used by all commands can be imported eagerly
- Type hints can use `TYPE_CHECKING` guards for eager imports without runtime cost:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kakitori.record import RecordResult  # Only for type checking
```

---

## Evolution

### Version 1 (2026-01-01)

Initial pattern established from CORE-001 retrofit.

---

## Related

- Promoted from: [../feature-designs/CORE-001.md](../feature-designs/CORE-001.md)
- Applied in: `src/kakitori/__init__.py`
