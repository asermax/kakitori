# ADR-004: Multi-Turn Chat for Long Recordings

**Status**: Superseded (see note below)
**Date**: 2026-01-01

## Superseded (2026-07-10)

This decision is no longer in effect. Kakitori dropped the Gemini transcription backend entirely in favor of Deepgram's nova-3 model. Deepgram's prerecorded API (`client.listen.v1.media.transcribe_file(...)`) transcribes a full recording — of any length recordings realistically reach — in a single synchronous request and returns all diarized utterances at once. There is no output-token ceiling forcing chunked continuation, so the multi-turn chat loop, its termination heuristic, and the checkpoint/resume gaps described below no longer apply to the codebase.

The rest of this document is preserved as-is for historical reference; it reflects the reasoning that applied while Gemini was the transcription backend.

## Context

Audio recordings of meetings and conversations can exceed 2 hours. Gemini's API has a `max_output_tokens` limit of 65536, which constrains how much transcription can be generated in a single request. We needed a strategy to transcribe recordings of arbitrary length.

## Decision

Use Gemini's chat API with a multi-turn conversation approach:

1. **First turn**: Send audio file + transcription prompt, request ~20 minutes of transcription
2. **Continuation turns**: Send continuation prompt, model transcribes next ~20 minutes
3. **Termination**: Model returns empty segments array when audio is exhausted

```python
chat = client.chats.create(model="gemini-3-flash-preview", config=...)

# First turn with audio
response = chat.send_message([audio_file, initial_prompt])
all_segments.extend(response.parsed.segments)

# Continue until empty array
while response.parsed.segments:
    response = chat.send_message(CONTINUATION_PROMPT)
    all_segments.extend(response.parsed.segments)
```

The chat session maintains context about the audio and speaker identities across turns.

## Consequences

### Positive

- Handles recordings of arbitrary length without preprocessing
- Maintains speaker identity context across turns (no re-detection per chunk)
- Model naturally progresses through audio without explicit time markers

### Negative

- Multiple API calls increase latency and cost
- Termination relies on model returning empty array (behavior not explicitly documented)
- No checkpoint/resume capability if interrupted mid-transcription

## Alternatives Considered

### Single request with max tokens

- **Description**: Request transcription in one call, accept truncation for long recordings
- **Why rejected**: Would silently drop content beyond token limit

### Time-based audio splitting

- **Description**: Split audio into 20-minute files, transcribe independently
- **Why rejected**: Complex audio processing, loses speaker continuity across boundaries

### Token counting with explicit chunking

- **Description**: Monitor output tokens, request specific time ranges
- **Why rejected**: Requires precise audio-to-token estimation, adds complexity

---

## Notes

- Retrofitted from PROCESS-001 implementation
- The ~20 minute chunk size is a prompt suggestion, not enforced; model determines actual boundaries
- Related: Temperature 0.3 prevents repetition loops during multi-turn (see design doc)
