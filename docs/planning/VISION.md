# Project Vision: Kakitori

**A CLI tool for recording and transcribing meetings with speaker diarization.**

## Problem

Recording meetings and conversations that mix local and remote participants (video calls, in-person discussions) produces audio that's difficult to transcribe.

**Who experiences this:**
- Remote workers recording video calls for later reference
- Meeting participants who want searchable transcripts with speaker attribution
- Anyone needing to transcribe audio with multiple speakers

**Current situation:**
- Standard recorders: Don't capture both microphone and system audio simultaneously
- Basic transcription tools: Lack speaker diarization (who said what)
- Manual identification: Require guessing speakers without audio playback for verification

**What's needed:**
A tool that records both audio sources, transcribes with speaker identification, and allows interactive verification of speaker names with audio snippet playback.

## Core Workflows

### 1. Record Audio

**Trigger**: User runs `kakitori record`
**Steps**:
1. User selects audio sources (microphone and/or system audio)
2. Tool creates PulseAudio combined sink to mix sources
3. User speaks/plays audio
4. User presses Ctrl+C to stop
5. Tool saves recording to file
6. Optionally prompts to transcribe immediately

**Result**: Single audio file containing all selected sources

### 2. Process Recording

**Trigger**: User runs `kakitori process <file>`
**Steps**:
1. Tool sends audio to Deepgram's nova-3 model in a single request
2. Deepgram returns diarized utterances for the entire recording at once
3. Tool identifies unique speakers in transcript
4. For each speaker, plays audio snippet from their first appearance
5. User provides name for each speaker
6. Tool generates final transcript with speaker names

**Result**: Readable transcript with timestamps and speaker attribution

### 3. Quick Transcribe (Legacy)

**Trigger**: User runs `kakitori <file>` (backwards compatible)
**Steps**:
1. Same as Process Recording workflow

**Result**: Same as Process Recording workflow

## Scope

### v1 Requirements - Implemented

All features are complete:

**Recording:**
- [x] Audio recording from microphone + system audio (RECORD-001)
- [x] PulseAudio combined sink for source mixing
- [x] Interactive source selection

**Transcription:**
- [x] Single-request AI transcription, handles recordings of any length (PROCESS-001)
- [x] Speaker diarization via Deepgram (nova-3)
- [x] Interactive speaker identification with audio playback

**CLI:**
- [x] Subcommand CLI with configuration priority (CORE-001)
- [x] Backwards-compatible invocation (`kakitori <file>`)
- [x] Multiple output options (file, stdout, custom path)

### Not Now

Explicitly out of scope:

**Platform:**
- [ ] macOS/Windows support (Linux-only via PulseAudio/PipeWire)

**Interface:**
- [ ] GUI interface (CLI-only)

**Features:**
- [ ] Real-time transcription (post-recording only)
- [ ] Multiple LLM backends (Deepgram-only)
- [ ] Audio editing or trimming
- [ ] Cloud storage integration

## Technical Context

**Privacy & Security:**
- Audio is sent to the Deepgram API for transcription
- API key stored in local config files
- No persistent cloud storage of recordings

**Platform:**
- Linux with PulseAudio or PipeWire
- Python 3.11+

**Installation/Deployment:**
- **uv tool**: `uv tool install kakitori` for global installation
- **Local dev**: `uv run kakitori` from project directory

**User Interaction:**
- CLI with subcommands (record, process)
- Interactive prompts for source selection and speaker naming
- Configuration via `.env` files

**External Systems:**
- Deepgram API (nova-3 model): Transcription with speaker diarization
- PulseAudio/PipeWire: Audio source management and recording
- ffmpeg: Audio encoding
- mpv: Audio playback for speaker identification

**Language/Runtime:**
- Python 3.11+
- No GPU requirements

**Dependencies (key):**
- `deepgram-sdk`: Deepgram API client
- `pydantic`: Data validation for internal transcription models
- `questionary`: Interactive prompts
- `rich`: Terminal formatting
- `python-mpv`: Audio playback
- `python-dotenv`: Configuration loading

**Setup Requirements:**
- System: ffmpeg, pactl, mpv binaries
- Configuration: `DEEPGRAM_API_KEY` in environment or `.env` file

## Success Criteria

v1 is successful when:
1. User can record a meeting with both microphone and system audio
2. Transcription correctly identifies different speakers
3. Speaker identification workflow allows verification via audio playback
4. Output is readable with timestamps and speaker names
5. Tool works on PulseAudio and PipeWire systems

## Future Considerations

Ideas for v2 and beyond (not committing to these):
- Support for additional LLM backends (local models, OpenAI)
- Real-time streaming transcription
- Speaker voice profiles for automatic identification
- Integration with note-taking apps
- Audio enhancement/noise reduction

---

**Project name**: "Kakitori" (書き取り) - Japanese for "dictation" or "transcription"
