# DES-003: Graceful ffmpeg Termination via stdin

**Scope**: Project-wide
**Date**: 2026-01-01
**Last Updated**: 2026-01-01

## Pattern

When running interactive ffmpeg recording, intercept SIGINT and write 'q' to ffmpeg's stdin instead of letting the signal propagate.

## Rationale

ffmpeg responds to 'q' by gracefully finishing the current frame and writing proper file trailers. Sending SIGINT directly can result in:
- Corrupted output files
- Missing audio container headers
- Truncated final frames

## Examples

### Do This

```python
import signal
import subprocess

def record_audio(source: str, output_path: Path) -> bool:
    process = subprocess.Popen(
        ["ffmpeg", "-f", "pulse", "-i", source, str(output_path)],
        stdin=subprocess.PIPE,
    )

    interrupted = False

    def handle_interrupt(signum, frame):
        nonlocal interrupted
        if interrupted:
            return  # Prevent double-handling
        interrupted = True

        # Graceful stop via stdin
        process.stdin.write(b"q")
        process.stdin.flush()
        process.stdin.close()

    original_handler = signal.signal(signal.SIGINT, handle_interrupt)

    try:
        process.wait()
    finally:
        signal.signal(signal.SIGINT, original_handler)

    return output_path.exists()
```

**Why**: ffmpeg properly finalizes the file with correct headers and duration metadata.

### Don't Do This

```python
def record_audio(source: str, output_path: Path) -> bool:
    process = subprocess.Popen(
        ["ffmpeg", "-f", "pulse", "-i", source, str(output_path)]
    )

    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()  # SIGTERM to ffmpeg

    return output_path.exists()
```

**Why**: SIGTERM/SIGINT to ffmpeg can corrupt the output file.

## Exceptions

- Non-interactive ffmpeg operations with `-t` duration limit
- Batch processing where file integrity can be verified afterward
- When intentionally aborting a recording that will be discarded

---

## Evolution

### Version 1 (2026-01-01)

Initial pattern established from RECORD-001 retrofit.

---

## Related

- Promoted from: [../designs/RECORD-001.md](../designs/RECORD-001.md)
- Applied in: `src/kakitori/record/recorder.py`
