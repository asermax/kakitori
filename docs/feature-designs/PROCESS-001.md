# Design: PROCESS-001 - Audio Transcription Processing

**Feature Spec**: [../feature-specs/PROCESS-001.md](../feature-specs/PROCESS-001.md)
**Status**: Approved

## Retrofit Note

This design was created from existing code at:
- `src/kakitori/process/command.py`
- `src/kakitori/process/transcribe.py`
- `src/kakitori/process/speaker.py`
- `src/kakitori/process/audio.py`
- `src/kakitori/process/output.py`
- `src/kakitori/models.py`

Original implementation date: Unknown (pre-framework)
Decisions documented during retrofit: ADR-004, DES-005, DES-006

---

## Purpose

This document captures the design rationale for the audio transcription feature, which produces timestamped transcripts with speaker attribution using AI-powered transcription.

## Problem Context

Users have audio recordings of conversations and need readable text transcripts with proper speaker attribution. The challenges are:

1. **Long recordings**: Meetings can exceed 2 hours; the transcription approach must handle full recordings reliably
2. **Speaker identification**: The provider only returns numbered labels ("Speaker 1") requiring human verification to assign real names
3. **Audio verification**: Users need to hear speaker voices to correctly assign names
4. **Reliable single-call transcription**: The transcription call must return complete, ordered results for the whole recording

**Constraints:**

- Audio snippet playback requires local mpv media player
- Deepgram's prerecorded API is synchronous; the request blocks until the full response is ready

## Design Overview

The processing workflow follows a three-stage pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Process Command Package                      │
│                                                                  │
│  Audio File                                                      │
│      │                                                           │
│      ▼                                                           │
│  ┌─────────────┐                                                │
│  │ TRANSCRIBE  │  transcribe.py                                 │
│  │             │  - Single request to Deepgram nova-3           │
│  │             │  - Diarized utterances returned in one response│
│  └──────┬──────┘                                                │
│         │ Transcription                                          │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │  IDENTIFY   │  speaker.py                                    │
│  │             │  - Paginated menu UI (DES-006)                 │
│  │             │  - Audio snippet playback                      │
│  │             │  - Adaptive duration (DES-005)                 │
│  └──────┬──────┘                                                │
│         │ speaker_mapping                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │   FORMAT    │  output.py                                     │
│  │             │  - [MM:SS] Speaker: content                    │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
```

**Module responsibilities:**

| Module | Responsibility |
|--------|----------------|
| `command.py` | Pipeline orchestration |
| `transcribe.py` | Deepgram API communication, single-request transcription |
| `speaker.py` | Interactive UI, speaker state management |
| `audio.py` | Timestamp parsing, mpv playback |
| `output.py` | Plain text formatting |
| `models.py` | Pydantic models for internal transcription data |

## Data Flow

### Single-Request Transcription

```
Audio File
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Transcribe                                          │
│   client = DeepgramClient(api_key=api_key)         │
│   response = client.listen.v1.media.transcribe_file(│
│       request=audio_bytes,                         │
│       model="nova-3",                              │
│       diarize=True,                                │
│       utterances=True,                             │
│       punctuate=True,                              │
│       detect_language=True,                        │
│   )                                                │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Convert Utterances                                  │
│   for utterance in response.results.utterances:    │
│       segments.append(TranscriptSegment(           │
│           start_time=format_timestamp(utterance.start),│
│           speaker=f"Speaker {utterance.speaker + 1}",│
│           content=utterance.transcript,             │
│       ))                                            │
└────────────────────────────────────────────────────┘
    │
    ▼
Transcription(segments=segments)
```

### Speaker Identification Flow

```
Transcription
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Build Speaker States                                │
│   For each unique speaker (always "Speaker N"):    │
│     - Extract segment indices                      │
│     - Create SpeakerState(label, name=None, indices)│
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Main Menu Loop                                      │
│   ┌──────────────────────────────┐                 │
│   │ Display Speaker Table        │                 │
│   │  Speaker 1  ???  (42 segs)   │                 │
│   │  John       ✓    (38 segs)   │                 │
│   └──────────────────────────────┘                 │
│   Select: speaker / confirm / cancel               │
└────────────────────────────────────────────────────┘
    │ (select speaker)
    ▼
┌────────────────────────────────────────────────────┐
│ Detail Menu (Paginated)                             │
│   Page 1 of 5 (42 segments)                        │
│   ┌─────────────────────────────────┐              │
│   │ #1  [00:15]  "Hello everyone..."│              │
│   │ #2  [01:42]  "I think we..."   │              │
│   │ ...                             │              │
│   └─────────────────────────────────┘              │
│   Actions: play / play page / next / assign / back │
└────────────────────────────────────────────────────┘
    │ (play snippet)
    ▼
┌────────────────────────────────────────────────────┐
│ Audio Playback                                      │
│   duration = min(next_segment_start - start, 5.0)  │
│   player.start = start_seconds                     │
│   player.end = start_seconds + duration            │
│   player.play(audio_path)                          │
└────────────────────────────────────────────────────┘
```

## Modeling

### Pydantic Models (Internal Data)

```python
class TranscriptSegment(BaseModel):
    start_time: str   # "MM:SS" or "HH:MM:SS"
    speaker: str      # "Speaker N" (Deepgram never returns names)
    content: str      # Verbatim transcription

class Transcription(BaseModel):
    segments: list[TranscriptSegment]
```

### Internal State

```python
@dataclass
class SpeakerState:
    label: str                    # Original label from transcription
    assigned_name: str | None     # User-assigned name
    segment_indices: list[int]    # Indices into transcription.segments
```

### Relationships

- `Transcription` is an internal data model built from Deepgram's response
- `SpeakerState` aggregates segment indices for navigation efficiency
- Speaker mapping (`dict[str, str]`) bridges original labels to user-assigned names

## Key Decisions

### Decision 1: Single-Request Transcription via Deepgram Prerecorded API

**Choice**: Send the whole audio file in one synchronous `transcribe_file` call rather than uploading, polling, and chunking across multiple conversation turns.

**Why**: Deepgram's prerecorded API processes recordings of any length (including 2+ hour meetings) in a single request and returns all diarized utterances at once, so there is no output-token ceiling to chunk around.

**Related**: [ADR-004](../architecture/ADR-004-multi-turn-transcription.md) (superseded — previously documented the Gemini multi-turn chat approach this replaces)

---

### Decision 2: Internal Pydantic Models for Normalized Output

**Choice**: Keep `TranscriptSegment`/`Transcription` as plain Pydantic models populated from Deepgram's response, rather than as a schema handed to the provider.

**Why**: Deepgram's `transcribe_file` returns its own typed response object (`response.results.utterances`); Pydantic here is only used to give the rest of the pipeline (speaker ID, formatting) a stable internal shape.

**Consequences**: Clean data flow; no dependency on a provider-side structured-output feature.

---

### Decision 4: Adaptive Snippet Duration

**Choice**: Calculate snippet duration based on next segment start, capped at 5 seconds.

**Why**: Prevents audio overlap into next speaker; short segments play completely.

**Related**: [DES-005](../design/DES-005-adaptive-snippet-duration.md)

---

### Decision 5: Two-Level Paginated Menu UI

**Choice**: Main menu shows speakers; detail menu shows paginated segments.

**Why**: Speakers with 100+ segments need pagination; overview + detail provides efficient navigation.

**Related**: [DES-006](../design/DES-006-paginated-menu-ui.md)

---

### Decision 6: Name Pre-Population Check Retained as a No-Op Under Deepgram

**Choice**: Keep the "pre-populate assigned_name if the label isn't a generic `Speaker \d+`" check in `speaker.py`, even though Deepgram always returns generic `Speaker N` labels.

**Why**: The check is harmless and provider-agnostic; it simply never triggers today because Deepgram has no name-inference capability. Real names always come from the interactive speaker-identification step.

**Implementation**: Check if label matches `Speaker \d+` pattern; if not, use label as assigned name (currently always false with Deepgram).

## System Behavior

### Scenario: Standard Transcription

```
Given: Audio file meeting.mp3 with 3 speakers
When: User runs `kakitori process meeting.mp3`
Then:
  1. Audio sent to Deepgram in a single request, transcribed in one response
  2. Speaker identification shows 3 speakers
  3. User plays snippets, assigns names
  4. Transcript saved to meeting.txt with names
```

### Scenario: Skip Speaker Identification

```
Given: A completed transcription with generic "Speaker N" labels
When: User runs `kakitori process meeting.mp3 --skip-speaker-id`
Then:
  1. Transcription generated
  2. Identification skipped
  3. Generic "Speaker N" labels preserved in output
```

### Scenario: User Cancels Identification

```
Given: Transcription with generic labels
When: User cancels identification
Then:
  1. Confirmation prompt shown
  2. Generic labels ("Speaker 1") preserved
  3. Transcript saved with generic labels
```

### Scenario: Stdout Output for Piping

```
Given: User needs transcript for downstream processing
When: User runs `kakitori process meeting.mp3 --stdout`
Then:
  1. Transcript printed to stdout (clean, no headers)
  2. No file written
  3. Suitable for `| grep` or other processing
```

## Notes

**Uncertainties:**

- Maximum recording length/file size Deepgram's prerecorded API reliably handles in a single request is unverified for this project's use cases
- Error recovery mid-transcription not implemented (single request either succeeds or fails as a whole)

**Assumptions:**

- Users have mpv installed for audio playback
- Deepgram API key has sufficient quota
- Supported formats: mp3, wav, m4a, ogg, flac

**Areas needing clarification:**

- Should very large/long files be split before sending to Deepgram, or is the single-request approach sufficient at all expected recording lengths?
