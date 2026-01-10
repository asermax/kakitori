# DES-004: Layered Cleanup with atexit + try/finally

**Scope**: Project-wide
**Date**: 2026-01-01
**Last Updated**: 2026-01-01

## Pattern

When managing external resources that persist beyond process termination (e.g., PulseAudio modules, temp files, network connections), use both `atexit` registration and `try/finally` blocks.

## Rationale

External resources may not be cleaned up automatically when a process ends:
- `try/finally` handles normal exceptions but not all termination scenarios
- `atexit` handlers run on normal exit but may miss some crash scenarios
- Using both maximizes cleanup coverage

## Examples

### Do This

```python
import atexit

def run_with_external_resource():
    resource = create_external_resource()

    # Register atexit as fallback for unexpected termination
    atexit.register(cleanup_resource, resource)

    try:
        # Use the resource
        do_work_with(resource)

    finally:
        # Normal cleanup path
        atexit.unregister(cleanup_resource)
        cleanup_resource(resource)
```

**Why**:
- `try/finally` handles exceptions during `do_work_with()`
- `atexit` handles unexpected termination (SIGTERM, other crashes)
- Unregistering after cleanup prevents double-cleanup

### Don't Do This

```python
def run_with_external_resource():
    resource = create_external_resource()

    try:
        do_work_with(resource)
    finally:
        cleanup_resource(resource)
```

**Why**: If process receives SIGTERM during `do_work_with()`, cleanup may not run.

```python
def run_with_external_resource():
    resource = create_external_resource()
    atexit.register(cleanup_resource, resource)

    do_work_with(resource)
    # No explicit cleanup - relies entirely on atexit
```

**Why**: Normal exceptions during `do_work_with()` would propagate without cleanup until exit.

## Exceptions

- Resources automatically cleaned up by the OS (file descriptors, memory)
- Short-lived operations where orphaned resources are acceptable
- When cleanup is expensive and the resource has a TTL

---

## Evolution

### Version 1 (2026-01-01)

Initial pattern established from RECORD-001 retrofit (PulseAudio module cleanup).

---

## Related

- Promoted from: [../feature-designs/RECORD-001.md](../feature-designs/RECORD-001.md)
- Related: [ADR-003](../architecture/ADR-003-pulseaudio-null-sink-mixing.md) (what needs cleanup)
- Applied in: `src/kakitori/record/command.py`
