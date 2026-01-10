# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Context

Kakitori is a CLI tool for audio recording and transcription with speaker diarization using Google's Gemini Flash model.

## Key Files

- `docs/planning/VISION.md` - Project vision and scope
- `docs/planning/FEATURES.md` - Feature inventory with status
- `docs/planning/DEPENDENCIES.md` - Implementation phases
- `docs/planning/BACKLOG.md` - Bugs, ideas, improvements, tech-debt, questions
- `docs/feature-specs/` - Feature specifications
- `docs/framework.md` - Development framework documentation

## Available Commands

Use `/vision`, `/features`, `/spec-feature`, `/design-feature`, `/plan-feature`, `/implement-feature` and other framework commands. See `docs/framework.md` for the full workflow.

**Backlog Management**:
- `/backlog [action]` - Manage bugs, ideas, improvements, tech-debt, questions
- `/review-code [context|BUG-ID|IMP-ID|DEBT-ID]` - Review code (supports backlog IDs)
- `/add-feature [description|IDEA-ID]` - Add feature (supports promoting IDEA items)
- `/decision [topic|Q-ID]` - Document decision (supports Q items)

## Backlog Tool

Use `scripts/backlog.py` to manage bugs, ideas, improvements, tech-debt, and questions.

```bash
python scripts/backlog.py list                           # List open items
python scripts/backlog.py show BUG-001                   # Show item details
python scripts/backlog.py add bug "Title" --priority 2   # Add new item
python scripts/backlog.py fix BUG-001 --commit abc123    # Mark as fixed
python scripts/backlog.py promote IDEA-001 --feature X   # Promote to feature
```

**Item types**: bug (BUG-), idea (IDEA-), improvement (IMP-), tech-debt (DEBT-), question (Q-)
**Priority scale**: 1=critical, 2=high, 3=medium, 4=low, 5=someday

## Current Focus

All features are implemented. Use `/analyze` for gap analysis.

---

## Project Overview

Kakitori is a CLI tool for audio recording and transcription with speaker diarization using Google's Gemini Flash model. It provides:
- Audio recording from microphone and system audio (PulseAudio/PipeWire + ffmpeg)
- Interactive workflow for speaker identification with audio snippet playback
- Transcription using Google's Gemini Flash model

## Command Line Interface

Kakitori uses a subcommand-based CLI:

```bash
# Record new audio
kakitori record [-o OUTPUT] [-v]

# Process existing audio file
kakitori process <file> [-o OUTPUT] [--stdout] [--skip-speaker-id] [-v]

# Backwards compatible (same as process)
kakitori <file> [options]
```

## Development Commands

### Local Development
```bash
# Install dependencies
uv sync

# Run the tool locally - record
uv run kakitori record

# Run the tool locally - process
uv run kakitori process recording.mp3

# Backwards compatible
uv run kakitori recording.mp3

# Install as a tool (for testing the installed version)
uv tool install . --reinstall
```

### Building
```bash
uv build
```

## Configuration

The tool supports multiple configuration sources with priority ordering:
1. System environment variables (highest priority)
2. Local `.env` file in current directory
3. Global config at `~/.config/kakitori/.env` (lowest priority)

API key is required: `GEMINI_API_KEY=your-key`

## Architecture

### Module Structure

The codebase follows a modular command-based architecture in `src/kakitori/`:

1. **Entry Point** (`__init__.py`):
   - Loads configuration from multiple sources (system env > local .env > global config)
   - Dispatches to subcommands: `record` or `process`
   - Sets up logging based on verbose flag

2. **CLI** (`cli.py`):
   - Subcommand-based argument parsing with argparse
   - `record` subcommand for audio recording
   - `process` subcommand for transcription
   - Backwards compatibility for `kakitori <file>` syntax

3. **Record Command** (`record/`):
   - `command.py`: Orchestrates recording workflow with combined sink lifecycle management
   - `sources.py`: PulseAudio/PipeWire source detection, combined sink creation and cleanup
   - `recorder.py`: ffmpeg process control with signal handling (single-source recording)
   - `ui.py`: Interactive source selection with questionary/rich

4. **Process Command** (`process/`):
   - `command.py`: Orchestrates transcription workflow (transcribe → identify speakers → format → save)

5. **Transcription** (`transcribe.py`):
   - Uploads audio to Gemini API
   - Uses Gemini Flash with structured output (Pydantic schema) for JSON responses
   - Currently configured: `gemini-flash-latest`, `max_output_tokens=65536` (supports ~2hr meetings)
   - Returns `(Transcription, file_name)` tuple for cleanup

6. **Speaker Identification** (`speaker.py`):
   - `identify_speakers()`: Interactive loop that plays audio snippets for each speaker
   - `get_snippet_duration()`: Calculates adaptive snippet duration (max 5s, bounded by next segment)
   - `apply_speaker_names()`: Maps generic labels (Speaker 1, Speaker 2) to user-provided names

7. **Audio Playback** (`audio.py`):
   - Uses `python-mpv` library to play audio snippets
   - `parse_timestamp()`: Converts MM:SS format to seconds
   - `play_snippet()`: Plays audio from start_seconds for specified duration

8. **Data Models** (`models.py`):
   - Pydantic models used as structured output schema for Gemini API
   - `TranscriptSegment`: Single segment with start_time, speaker, content
   - `Transcription`: List of segments

9. **Output Formatting** (`output.py`):
   - Formats transcription as plain text with timestamps and speaker names
   - Format: `[MM:SS] Speaker: content`

10. **Logging** (`logging.py`):
    - Configured to output to stderr (keeps stdout clean for transcript output)
    - INFO level by default, DEBUG level with `-v` flag
    - Format: `[LEVEL] message`

### Key Design Decisions

- **Subcommand CLI**: Separate `record` and `process` commands with backwards compatibility
- **Command Packages**: Each command has its own package (record/, process/) with command logic and helpers
- **PulseAudio Combined Sink**: Uses temporary null sink with loopbacks to mix microphone and system audio at the audio server level, eliminating timestamp synchronization issues that occur with dual-source ffmpeg mixing
- **Structured Output**: Uses Pydantic models with Gemini's `response_schema` parameter for reliable JSON parsing
- **Adaptive Snippets**: Speaker identification snippets adjust duration based on next segment to avoid overlap
- **Interactive UI**: Uses questionary/rich for consistent interactive menus across speaker ID and source selection
- **Config Priority**: Supports global config directory to avoid per-directory .env files while allowing local overrides
- **Logging to stderr**: All logs go to stderr so `--stdout` flag can output clean transcript to stdout for piping
- **Optional Transcription**: After recording, prompts user to transcribe immediately (requires GEMINI_API_KEY)

## Dependencies

- `google-genai`: Gemini API client
- `pydantic`: Data validation and structured output schema
- `python-dotenv`: Multi-source .env file loading
- `python-mpv`: Audio playback (requires `mpv` system binary)

## System Requirements

- Python 3.11+
- `mpv` media player (for audio snippet playback during speaker identification)
- `pactl` (PulseAudio/PipeWire utils - for audio recording)
- `ffmpeg` with PulseAudio support (for audio recording)
