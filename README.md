# Kakitori

CLI tool for audio recording and transcription with speaker diarization using Deepgram's nova-3.

## Installation

```bash
uv tool install kakitori
```

Requires `mpv` and `pactl`/`ffmpeg` (for recording) installed on your system.

## Configuration

Add your Deepgram API key to `~/.config/kakitori/.env`:

```bash
DEEPGRAM_API_KEY=your-api-key-here
```

## Usage

### Record and transcribe

```bash
kakitori record
```

### Transcribe an existing file

```bash
kakitori process recording.mp3
```

### Options

```bash
kakitori process recording.mp3 -o transcript.txt   # save to file
kakitori process recording.mp3 --stdout             # output to stdout
kakitori process recording.mp3 --skip-speaker-id    # skip speaker identification
```

## Output

```
[00:15] John: Hello everyone, welcome to today's meeting.
[00:32] Jane: Thanks for having me. I have some updates to share.
```

## License

MIT
