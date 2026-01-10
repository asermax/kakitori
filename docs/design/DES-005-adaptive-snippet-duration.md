# DES-005: Adaptive Snippet Duration

**Scope**: Project-wide
**Date**: 2026-01-01
**Last Updated**: 2026-01-01

## Pattern

When playing audio snippets from transcription segments, calculate duration based on the next segment's start time, capped at a maximum value.

## Rationale

Fixed-duration snippets cause problems:
- Too long: Plays into the next speaker's segment, confusing the user
- Too short: May not capture enough context for identification

Adaptive duration solves this:
- Short segments (< max) play completely
- Long segments play a representative sample
- Never overlaps into the next speaker

## Examples

### Do This

```python
def get_snippet_duration(
    segments: list[TranscriptSegment],
    current_index: int,
    max_duration: float = 5.0,
) -> float:
    """Duration capped at next segment start or max_duration."""
    current_start = parse_timestamp(segments[current_index].start_time)

    if current_index + 1 < len(segments):
        next_start = parse_timestamp(segments[current_index + 1].start_time)
        return min(next_start - current_start, max_duration)

    return max_duration  # Last segment uses max


# Usage
duration = get_snippet_duration(transcription.segments, segment_idx)
play_snippet(audio_path, start_seconds, duration=duration)
```

**Why**: A 2-second segment between speakers plays for 2 seconds. A 30-second monologue plays for 5 seconds. Neither overlaps.

### Don't Do This

```python
def play_segment_snippet(segment, audio_path):
    start = parse_timestamp(segment.start_time)
    play_snippet(audio_path, start, duration=5.0)  # Fixed duration
```

**Why**: If the segment is only 1.5 seconds, the snippet will include 3.5 seconds of the next speaker.

## Exceptions

- When playing for enjoyment rather than identification (user might want full segment)
- When segments don't have reliable timestamps
- When audio analysis can detect speaker changes dynamically

---

## Evolution

### Version 1 (2026-01-01)

Initial pattern established from PROCESS-001 retrofit.

---

## Related

- Promoted from: [../feature-designs/PROCESS-001.md](../feature-designs/PROCESS-001.md)
- Applied in: `src/kakitori/process/speaker.py`
