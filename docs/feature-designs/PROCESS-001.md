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

1. **Long recordings**: Meetings can exceed 2 hours, but API output limits constrain single-request transcription
2. **Speaker identification**: AI may use generic labels ("Speaker 1") requiring human verification
3. **Audio verification**: Users need to hear speaker voices to correctly assign names
4. **File management**: Uploaded audio files consume API storage and need cleanup

**Constraints:**

- Gemini API has 65536 max output tokens limit
- Audio snippet playback requires local mpv media player
- Temperature tuning critical (too low causes repetition loops)

## Design Overview

The processing workflow follows a four-stage pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Process Command Package                      │
│                                                                  │
│  Audio File                                                      │
│      │                                                           │
│      ▼                                                           │
│  ┌─────────────┐                                                │
│  │ TRANSCRIBE  │  transcribe.py                                 │
│  │             │  - Upload to Gemini API                        │
│  │             │  - Multi-turn chat (ADR-004)                   │
│  │             │  - Structured output (Pydantic)                │
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
│  └──────┬──────┘                                                │
│         │ formatted text                                         │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │   CLEANUP   │  transcribe.py                                 │
│  │             │  - Delete from Gemini API                      │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
```

**Module responsibilities:**

| Module | Responsibility |
|--------|----------------|
| `command.py` | Pipeline orchestration |
| `transcribe.py` | Gemini API communication, multi-turn transcription |
| `speaker.py` | Interactive UI, speaker state management |
| `audio.py` | Timestamp parsing, mpv playback |
| `output.py` | Plain text formatting |
| `models.py` | Pydantic schemas for structured output |

## Data Flow

### Multi-Turn Transcription

```
Audio File
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Upload & Wait                                       │
│   client.files.upload(file=audio_path)             │
│   while state == "PROCESSING": poll                │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Chat Session Setup                                  │
│   chat = client.chats.create(                      │
│       model="gemini-3-flash-preview",              │
│       config={                                     │
│           response_schema=Transcription,           │
│           temperature=0.3,                         │
│           max_output_tokens=65536                  │
│       }                                            │
│   )                                                │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Turn 1: Audio + Initial Prompt                      │
│   response = chat.send_message([audio, prompt])    │
│   all_segments.extend(response.parsed.segments)    │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Turn N: Continuation Loop                           │
│   while response.parsed.segments:                  │
│       response = chat.send_message(CONTINUATION)   │
│       all_segments.extend(segments)                │
│                                                    │
│   Stop when: empty segments array                  │
└────────────────────────────────────────────────────┘
    │
    ▼
Transcription(segments=all_segments)
```

### Speaker Identification Flow

```
Transcription
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Build Speaker States                                │
│   For each unique speaker:                         │
│     - Extract segment indices                      │
│     - Pre-populate name if AI detected one         │
│     - Create SpeakerState(label, name, indices)    │
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

### Pydantic Models (Gemini Structured Output)

```python
class TranscriptSegment(BaseModel):
    start_time: str   # "MM:SS" or "HH:MM:SS"
    speaker: str      # Name or "Speaker N"
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

- `Transcription` is the API response schema and internal data model
- `SpeakerState` aggregates segment indices for navigation efficiency
- Speaker mapping (`dict[str, str]`) bridges original labels to user-assigned names

## Key Decisions

### Decision 1: Multi-Turn Chat for Long Recordings

**Choice**: Use Gemini chat API with continuation prompts rather than single-request transcription.

**Why**: Recordings can exceed 2 hours; single request would truncate at token limit.

**Related**: [ADR-004](../architecture/ADR-004-multi-turn-transcription.md)

---

### Decision 2: Pydantic Structured Output Schema

**Choice**: Use Pydantic models with Gemini's `response_schema` parameter.

**Why**: Eliminates fragile JSON parsing; provides type-safe, validated responses.

**Consequences**: Clean data flow, but tied to Gemini's structured output feature.

---

### Decision 3: Temperature 0.3 to Prevent Repetition Loops

**Choice**: Use temperature=0.3 rather than temperature=0.

**Why**: Temperature=0 caused infinite repetition loops in multi-turn transcription.

**Consequences**: Reliable completion with minor non-determinism.

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

### Decision 6: AI Name Pre-Population

**Choice**: Pre-populate speaker names when AI detects them from conversation context.

**Why**: AI often identifies speakers correctly from introductions or name mentions. Pre-populating saves user effort.

**Implementation**: Check if label matches `Speaker \d+` pattern; if not, use label as assigned name.

## System Behavior

### Scenario: Standard Transcription

```
Given: Audio file meeting.mp3 with 3 speakers
When: User runs `kakitori process meeting.mp3`
Then:
  1. Audio uploaded, transcribed across N turns
  2. Speaker identification shows 3 speakers
  3. User plays snippets, assigns names
  4. Transcript saved to meeting.txt with names
  5. Uploaded file deleted from Gemini
```

### Scenario: Skip Speaker Identification

```
Given: Recording where AI detected speaker names
When: User runs `kakitori process meeting.mp3 --skip-speaker-id`
Then:
  1. Transcription generated
  2. Identification skipped
  3. AI-detected names preserved in output
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

- Model's decision to return empty segments array is not explicitly documented
- Maximum recording length that multi-turn reliably handles unknown
- Error recovery mid-transcription not implemented

**Assumptions:**

- Users have mpv installed for audio playback
- Gemini API key has sufficient quota
- Supported formats: mp3, wav, m4a, ogg, flac

**Areas needing clarification:**

- Should continuation prompt include context about where model left off?
- How to detect and handle skipped audio sections?
- Checkpoint/resume for interrupted long transcriptions?
