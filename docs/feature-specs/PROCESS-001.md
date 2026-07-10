# PROCESS-001: Audio Transcription Processing

## Retrofit Note

This spec was created from existing code at `src/kakitori/process/`.

---

## User Story

As a user with an audio recording,
I want to transcribe the audio with speaker diarization and identify who said what,
So that I have a readable text transcript with proper speaker attribution.

## Behavior

The process feature takes an audio file and produces a timestamped transcript with speaker labels. It uses Deepgram's nova-3 model for AI-powered transcription with automatic speaker diarization. The workflow consists of three main steps:

1. **Transcription**: The audio file is sent to Deepgram's prerecorded API in a single synchronous request and transcribed with diarized utterances (speaker index, start/end times, transcript text) returned all at once, regardless of recording length.

2. **Interactive Speaker Identification**: After transcription, users can optionally review and assign names to speakers through an interactive menu that plays audio snippets for verification.

3. **Output Formatting**: The transcript is formatted as plain text with timestamps and speaker labels.

## Acceptance Criteria

### Basic Transcription

- Given an audio file exists at the specified path
  When the user runs `kakitori process <audio_file>`
  Then the audio is sent to Deepgram's prerecorded API in a single request
  And the transcription is performed with speaker diarization
  And the user is prompted to identify speakers
  And a text file is saved with the same name as the audio file (with .txt extension)

### Transcription for Recordings of Any Length

- Given an audio recording of any length (including recordings exceeding 2 hours)
  When transcription is performed
  Then the system sends a single `transcribe_file` request to Deepgram
  And Deepgram returns all diarized utterances for the entire recording in one response
  And all utterances are converted into transcription segments in chronological order

### Custom Output Path

- Given the user specifies `-o <path>` option
  When transcription completes
  Then the transcript is saved to the specified path instead of the default

### Stdout Output

- Given the user specifies `--stdout` flag
  When transcription completes
  Then the transcript is printed to stdout with a header
  And no file is written to disk

### Skip Speaker Identification

- Given the user specifies `--skip-speaker-id` flag
  When transcription completes
  Then the interactive speaker identification is skipped
  And generic speaker labels (Speaker 1, Speaker 2, ...) are preserved

### Speaker Identification with Audio Playback

- Given a transcription with multiple speakers
  When the user enters speaker identification
  Then a table shows all detected speakers with their status
  And the user can select any speaker to see their segments
  And the user can play audio snippets to verify speaker identity
  And the user can assign names to speakers
  (Deepgram speakers are numbered only — e.g. "Speaker 1", "Speaker 2" — real names
  always come from this interactive step, never from the transcription provider)

### Paginated Segment View

- Given a speaker has more than 10 segments
  When viewing that speaker's detail menu
  Then segments are paginated with 10 per page
  And the user can navigate between pages
  And the user can play all snippets on the current page

### Adaptive Snippet Duration

- Given a segment is followed by another segment
  When playing an audio snippet
  Then the duration is capped at the start of the next segment or 5 seconds (whichever is smaller)

### Error Cases

- Given DEEPGRAM_API_KEY is not configured
  When the user runs the process command
  Then an error message is displayed explaining how to configure the key

- Given the specified audio file does not exist
  When the user runs the process command
  Then an error message is displayed

- Given Deepgram returns an error response
  When processing completes
  Then an exception is raised with the error details from Deepgram

## Dependencies

### Python Dependencies

- `deepgram-sdk` - Deepgram API client for transcription
- `pydantic` - Internal data models for transcription segments
- `questionary` - Interactive prompts and menus
- `rich` - Terminal UI tables and formatting
- `python-mpv` - Audio snippet playback

### System Requirements

- `mpv` binary - Required for audio playback during speaker identification
- Network access to Deepgram API
- `DEEPGRAM_API_KEY` configured (env, local .env, or ~/.config/kakitori/.env)

## Technical Notes

### Supported Audio Formats

- MP3 (audio/mpeg)
- WAV (audio/wav)
- M4A (audio/mp4)
- OGG (audio/ogg)
- FLAC (audio/flac)

### Model Configuration

- Model: `nova-3`
- Request options: `diarize=True`, `utterances=True`, `punctuate=True`, `detect_language=True`
- Single synchronous `transcribe_file` call — no polling, no per-turn continuation

### Output Format

```
[MM:SS] Speaker: content
[MM:SS] Speaker: content
...
```

### Design Decisions

- **Single-request transcription**: Deepgram's prerecorded API handles recordings of arbitrary length in one call, so there is no chunking or continuation loop to manage
- **Numbered speakers only**: Deepgram diarization returns numbered speakers (Speaker 1, Speaker 2, ...) with no name inference; real names always come from the interactive speaker-identification step
- **Adaptive snippets**: Duration bounded by next segment to avoid audio overlap during playback
