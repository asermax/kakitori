# PROCESS-001: Audio Transcription Processing

## Retrofit Note

This spec was created from existing code at `src/kakitori/process/`.

---

## User Story

As a user with an audio recording,
I want to transcribe the audio with speaker diarization and identify who said what,
So that I have a readable text transcript with proper speaker attribution.

## Behavior

The process feature takes an audio file and produces a timestamped transcript with speaker labels. It uses Google's Gemini Flash model for AI-powered transcription with automatic speaker diarization. The workflow consists of four main steps:

1. **Audio Upload and Transcription**: The audio file is uploaded to Gemini's API and transcribed using a multi-turn conversation approach to handle recordings of any length.

2. **Interactive Speaker Identification**: After transcription, users can optionally review and assign names to speakers through an interactive menu that plays audio snippets for verification.

3. **Output Formatting**: The transcript is formatted as plain text with timestamps and speaker labels.

4. **Cleanup**: The uploaded audio file is deleted from Gemini's servers.

## Acceptance Criteria

### Basic Transcription

- Given an audio file exists at the specified path
  When the user runs `kakitori process <audio_file>`
  Then the audio is uploaded to Gemini API
  And the transcription is performed with speaker diarization
  And the user is prompted to identify speakers
  And a text file is saved with the same name as the audio file (with .txt extension)

### Multi-Turn Transcription for Long Recordings

- Given an audio recording longer than ~20 minutes
  When transcription is performed
  Then the system uses multiple conversation turns to process the entire recording
  And each turn transcribes approximately 20 minutes of audio
  And the system continues until an empty segments array is returned
  And all segments are combined into a single transcription

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
  And generic speaker labels (Speaker 1, Speaker 2) or AI-detected names are preserved

### Participant Count

- Given the user specifies `-p <count>` option
  When transcription starts
  Then the participant count is passed to the AI for better diarization

- Given the user does not specify `-p` option
  When the process command starts
  Then the user is prompted to enter the number of participants

### Speaker Identification with Audio Playback

- Given a transcription with multiple speakers
  When the user enters speaker identification
  Then a table shows all detected speakers with their status
  And the user can select any speaker to see their segments
  And the user can play audio snippets to verify speaker identity
  And the user can assign names to speakers
  And speakers with AI-detected names are pre-populated

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

- Given GEMINI_API_KEY is not configured
  When the user runs the process command
  Then an error message is displayed explaining how to configure the key

- Given the specified audio file does not exist
  When the user runs the process command
  Then an error message is displayed

- Given Gemini reports the file processing state as "FAILED"
  When processing completes
  Then an exception is raised with "Audio file processing failed"

- Given the AI returns an invalid or empty response
  When parsing the transcription
  Then an exception is raised with the turn number, finish reason, and response text

## Dependencies

### Python Dependencies

- `google-genai` - Google Gemini API client for transcription
- `pydantic` - Data validation and structured output schema
- `questionary` - Interactive prompts and menus
- `rich` - Terminal UI tables and formatting
- `python-mpv` - Audio snippet playback

### System Requirements

- `mpv` binary - Required for audio playback during speaker identification
- Network access to Gemini API
- `GEMINI_API_KEY` configured (env, local .env, or ~/.config/kakitori/.env)

## Technical Notes

### Supported Audio Formats

- MP3 (audio/mpeg)
- WAV (audio/wav)
- M4A (audio/mp4)
- OGG (audio/ogg)
- FLAC (audio/flac)

### Model Configuration

- Model: `gemini-3-flash-preview`
- Temperature: 0.3 (low but non-zero to prevent repetition loops)
- Max output tokens: 65536
- Structured output via Pydantic schema

### Output Format

```
[MM:SS] Speaker: content
[MM:SS] Speaker: content
...
```

### Design Decisions

- **Multi-turn approach**: Handles recordings of arbitrary length by processing ~20 minutes per turn, avoiding token limits
- **AI name detection**: Speaker detection attempts to infer names from conversation context before falling back to generic labels
- **Temperature 0.3**: Tuned to prevent repetition loops while maintaining accuracy
- **Adaptive snippets**: Duration bounded by next segment to avoid audio overlap during playback
