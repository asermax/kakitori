# Kakitori

Audio transcription with speaker diarization using Gemini Flash.

## Overview

Kakitori is a CLI tool that transcribes audio files with speaker diarization using Google's Gemini 2.5 Flash model. It provides an interactive workflow to identify speakers by playing audio snippets and allows you to assign names to each speaker.

## Features

- **Audio Transcription**: Upload and transcribe audio files using Gemini 2.5 Flash
- **Speaker Diarization**: Automatically identify different speakers in the audio
- **Interactive Speaker Identification**: Listen to audio snippets and assign names to speakers
- **Multiple Audio Formats**: Supports MP3, WAV, M4A, OGG, FLAC
- **Plain Text Output**: Generate clean, readable transcripts with timestamps

## Requirements

- Python 3.11+
- `mpv` media player installed on your system
  - **macOS**: `brew install mpv`
  - **Linux (Arch)**: `pacman -S mpv`
  - **Linux (Debian/Ubuntu)**: `apt install mpv`
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Installation

### As a uv tool (recommended)

```bash
uv tool install kakitori
```

### From source

```bash
git clone <repository-url>
cd kakitori
uv sync
```

## Configuration

Create a `.env` file in your working directory with your Gemini API key:

```bash
GEMINI_API_KEY=your-api-key-here
```

Or set it as an environment variable:

```bash
export GEMINI_API_KEY=your-api-key-here
```

## Usage

### Basic usage

Transcribe an audio file and print to stdout:

```bash
kakitori recording.mp3
```

### Save to file

Save the transcript to a file:

```bash
kakitori recording.mp3 -o transcript.txt
```

### Skip speaker identification

Skip the interactive speaker identification step and keep generic labels:

```bash
kakitori recording.mp3 --skip-speaker-id
```

## Interactive Speaker Identification

When you run `kakitori` without `--skip-speaker-id`, the tool will:

1. Upload and transcribe your audio file
2. Identify unique speakers (Speaker 1, Speaker 2, etc.)
3. For each speaker:
   - Play 3-5 audio snippets where that speaker talks
   - Show a preview of what they said
   - Prompt you to assign a name

Example interaction:

```
Speaker 1:
--------------------------------------------------

Playing 3 snippet(s) for Speaker 1...

Snippet 1/3: [00:15]
  "Hello everyone, welcome to today's meeting..."

[Audio plays]

Snippet 2/3: [02:30]
  "I think we should focus on the quarterly goals..."

[Audio plays]

Who is Speaker 1? (press Enter to replay, or type name): John
✓ Speaker 1 identified as: John
```

## Output Format

The transcript is formatted as plain text with timestamps and speaker names:

```
[00:15] John: Hello everyone, welcome to today's meeting.
[00:32] Jane: Thanks for having me. I have some updates to share.
[01:05] John: Great, let's hear them.
[01:10] Jane: First, the project timeline has been extended...
```

## Development

### Running locally

```bash
# Install dependencies
uv sync

# Run the tool
uv run kakitori recording.mp3
```

### Building

```bash
uv build
```

## License

MIT

## Credits

Built with:
- [Google Gemini API](https://ai.google.dev/gemini-api)
- [python-mpv](https://github.com/jaseg/python-mpv)
- [Pydantic](https://docs.pydantic.dev/)
