# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kakitori is a CLI tool for audio transcription with speaker diarization using Google's Gemini Flash model. It provides an interactive workflow where users can listen to audio snippets and assign names to speakers.

## Development Commands

### Local Development
```bash
# Install dependencies
uv sync

# Run the tool locally
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

The codebase follows a modular pipeline architecture in `src/kakitori/`:

1. **Entry Point** (`__init__.py`):
   - Loads configuration from multiple sources (system env > local .env > global config)
   - Orchestrates the main workflow: transcribe → identify speakers → format → save/output
   - Sets up logging based on verbose flag

2. **CLI** (`cli.py`):
   - Argument parsing with argparse
   - Validates audio file exists before proceeding

3. **Transcription** (`transcribe.py`):
   - Uploads audio to Gemini API
   - Uses Gemini Flash with structured output (Pydantic schema) for JSON responses
   - Currently configured: `gemini-flash-latest`, `max_output_tokens=65536` (supports ~2hr meetings)
   - Returns `(Transcription, file_name)` tuple for cleanup

4. **Speaker Identification** (`speaker.py`):
   - `identify_speakers()`: Interactive loop that plays audio snippets for each speaker
   - `get_snippet_duration()`: Calculates adaptive snippet duration (max 5s, bounded by next segment)
   - `apply_speaker_names()`: Maps generic labels (Speaker 1, Speaker 2) to user-provided names

5. **Audio Playback** (`audio.py`):
   - Uses `python-mpv` library to play audio snippets
   - `parse_timestamp()`: Converts MM:SS format to seconds
   - `play_snippet()`: Plays audio from start_seconds for specified duration

6. **Data Models** (`models.py`):
   - Pydantic models used as structured output schema for Gemini API
   - `TranscriptSegment`: Single segment with start_time, speaker, content
   - `Transcription`: List of segments

7. **Output Formatting** (`output.py`):
   - Formats transcription as plain text with timestamps and speaker names
   - Format: `[MM:SS] Speaker: content`

8. **Logging** (`logging.py`):
   - Configured to output to stderr (keeps stdout clean for transcript output)
   - INFO level by default, DEBUG level with `-v` flag
   - Format: `[LEVEL] message`

### Key Design Decisions

- **Structured Output**: Uses Pydantic models with Gemini's `response_schema` parameter for reliable JSON parsing
- **Adaptive Snippets**: Speaker identification snippets adjust duration based on next segment to avoid overlap
- **Config Priority**: Supports global config directory to avoid per-directory .env files while allowing local overrides
- **Logging to stderr**: All logs go to stderr so `--stdout` flag can output clean transcript to stdout for piping

## Dependencies

- `google-genai`: Gemini API client
- `pydantic`: Data validation and structured output schema
- `python-dotenv`: Multi-source .env file loading
- `python-mpv`: Audio playback (requires `mpv` system binary)

## System Requirements

- Python 3.11+
- `mpv` media player must be installed on the system for audio playback
