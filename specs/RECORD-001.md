# RECORD-001: Audio Recording with Combined Sources

## Retrofit Note

This spec was created from existing code at `src/kakitori/record/`.

---

## User Story

As a user who wants to record meetings or calls,
I want to capture both my microphone input and system audio (e.g., video call audio) into a single recording,
So that I can later transcribe conversations that include both local and remote participants.

## Behavior

The record feature provides an interactive workflow for recording audio from multiple sources on Linux systems using PulseAudio/PipeWire. It automatically detects available audio sources, allows the user to select or confirm which microphone and system audio monitor to use, then creates a temporary combined audio sink that mixes both sources into a single stream. The recording is captured using ffmpeg with the Opus codec and saved as an OGG file. After recording completes, the user can optionally proceed to transcription if a Gemini API key is configured.

## Acceptance Criteria

### Dependency Validation

- Given the system does not have `pactl` installed
  When the user runs `kakitori record`
  Then an error is displayed listing "pactl" as missing
  And the command exits without recording

- Given the system does not have `ffmpeg` installed
  When the user runs `kakitori record`
  Then an error is displayed listing "ffmpeg" as missing
  And the command exits without recording

- Given both `pactl` and `ffmpeg` are missing
  When the user runs `kakitori record`
  Then an error is displayed listing both as missing
  And an installation hint is shown: "Install with: sudo pacman -S pulseaudio-utils ffmpeg"

### Source Detection

- Given PulseAudio/PipeWire is running
  When the record workflow starts
  Then available audio sources are retrieved via `pactl list short sources`
  And sources are categorized into inputs (microphones) and monitors (system audio)

- Given no input sources are available
  When the record workflow starts
  Then an error "No input sources found" is displayed
  And the command exits without recording

- Given no monitor sources are available
  When the record workflow starts
  Then an error "No monitor sources found" is displayed
  And the command exits without recording

### Source Selection

- Given audio sources are available
  When the user has not specified sources
  Then the first RUNNING input source is pre-selected (or first available if none running)
  And the first RUNNING monitor source is pre-selected (or first available if none running)

- Given sources are pre-selected
  When the source confirmation UI is displayed
  Then a rich table shows the selected sources with their state (RUNNING indicator)
  And options are provided to: continue, change input, or change monitor

- Given the user cancels source selection (Ctrl+C or ESC)
  When at the source confirmation step
  Then "Recording cancelled" is logged
  And the command exits without recording

### Output Path Handling

- Given the user provides `-o output.ogg`
  When the recording workflow starts
  Then the specified path is used for the output file

- Given the user provides `-o output` (no extension)
  When the recording workflow starts
  Then `.ogg` extension is appended automatically

- Given no output path is provided
  When the recording workflow starts
  Then the user is prompted for a filename
  And a default name is suggested: `recording_YYYYMMDD_HHMMSS.ogg`

### Combined Sink Creation

- Given valid input and monitor sources are selected
  When the combined sink is created
  Then a PulseAudio null sink named "kakitori_combined" is created (48kHz, stereo)
  And a loopback module routes the input source to the null sink
  And a loopback module routes the monitor source to the null sink

- Given null sink or loopback creation fails
  When attempting to create the combined sink
  Then previously created modules are cleaned up
  And an appropriate error is displayed
  And the command exits without recording

### Recording Process

- Given the combined sink is ready
  When recording starts
  Then ffmpeg is invoked with PulseAudio input from the combined sink monitor
  And the Opus codec (`libopus`) is used for audio encoding
  And recording is written to a temp file in `/tmp/`
  And "Starting recording... Press Ctrl+C to stop." is displayed

- Given recording is in progress
  When the user presses Ctrl+C
  Then the ffmpeg process receives a graceful 'q' command to stop
  And the recording is finalized properly
  And the temp file is moved to the final output path
  And a success message shows the output path

### Cleanup Handling

- Given the combined sink has been created
  When the recording workflow completes (success or failure)
  Then all PulseAudio modules (loopbacks, null sink) are unloaded

- Given the combined sink has been created
  When the process is terminated unexpectedly
  Then the atexit handler ensures cleanup is performed

### Post-Recording Transcription

- Given a Gemini API key is configured
  When recording completes successfully
  Then the user is prompted "Transcribe the recording now?"

- Given the user confirms transcription
  When prompted
  Then the user is asked for the participant count
  And the process command is invoked with the recording file

## Dependencies

### System Dependencies

- `pactl` - PulseAudio/PipeWire command-line tool for source detection and sink management
- `ffmpeg` - Audio recording with PulseAudio input support and Opus codec

### Python Dependencies

- `questionary` - Interactive prompts and menus
- `rich` - Console output and table formatting

## Technical Notes

### Combined Sink Architecture

The implementation uses a PulseAudio null sink with two loopback modules to mix audio at the audio server level. This approach eliminates timestamp synchronization issues that would occur with dual-source ffmpeg mixing. The combined sink monitor source provides a single stream containing both microphone and system audio.

### Signal Handling

SIGINT (Ctrl+C) is intercepted to gracefully stop ffmpeg by writing 'q' to its stdin. A flag prevents double-handling of the interrupt signal. The original signal handler is restored after recording completes.

### Temp File Strategy

Recording writes to `/tmp/` first, then moves to the final location on success. This prevents partial files from appearing at the destination if recording fails or is interrupted before finalization.
