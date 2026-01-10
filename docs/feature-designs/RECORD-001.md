# Design: RECORD-001 - Audio Recording with Combined Sources

**Feature Spec**: [../feature-specs/RECORD-001.md](../feature-specs/RECORD-001.md)
**Status**: Approved

## Retrofit Note

This design was created from existing code at:
- `src/kakitori/record/command.py`
- `src/kakitori/record/sources.py`
- `src/kakitori/record/recorder.py`
- `src/kakitori/record/ui.py`

Original implementation date: Unknown (pre-framework)
Decisions documented during retrofit: ADR-003, DES-002, DES-003, DES-004

---

## Purpose

This document captures the design rationale for the audio recording feature, which captures mixed microphone and system audio on Linux systems.

## Problem Context

Recording meetings and conversations that mix local and remote participants requires capturing both microphone input (local speaker) and system audio (remote participants via video call). Linux audio systems (PulseAudio/PipeWire) provide separate streams for these sources.

**Challenges addressed:**

1. **Source combination**: Microphone and system audio are separate streams that must be merged
2. **Timestamp synchronization**: Dual-source recording causes drift over long sessions
3. **Resource cleanup**: PulseAudio modules persist beyond process termination
4. **Graceful termination**: Recording must be stoppable without corrupting output

**Constraints:**

- Platform-specific: Linux with PulseAudio or PipeWire
- Requires external tools: `pactl` for audio routing, `ffmpeg` for recording
- Interactive terminal environment for source selection

## Design Overview

The recording feature orchestrates a multi-step workflow through four collaborating modules:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Record Command Package                        │
│                                                                  │
│  ┌────────────────┐                                             │
│  │   command.py   │  Orchestrator                               │
│  │                │  - Dependency check                         │
│  │  run_record()  │  - Source discovery                         │
│  │                │  - Workflow coordination                    │
│  │                │  - Cleanup management                       │
│  └───────┬────────┘                                             │
│          │                                                       │
│    ┌─────┴─────┬──────────────┐                                 │
│    ▼           ▼              ▼                                 │
│  ┌──────┐  ┌──────────┐  ┌──────────┐                          │
│  │ ui.py│  │sources.py│  │recorder. │                          │
│  │      │  │          │  │   py     │                          │
│  │Tables│  │PulseAudio│  │  ffmpeg  │                          │
│  │Prompts│ │Modules   │  │  Signal  │                          │
│  └──────┘  └──────────┘  └──────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

**Module responsibilities:**

| Module | Responsibility |
|--------|----------------|
| `command.py` | Workflow orchestration, cleanup coordination |
| `sources.py` | PulseAudio introspection, combined sink lifecycle |
| `recorder.py` | ffmpeg subprocess, signal handling |
| `ui.py` | Interactive prompts, rich table display |

## Data Flow

### Execution Sequence

```
User: kakitori record
         │
         ▼
┌─────────────────────────────────────┐
│ 1. VALIDATION                       │
│    check_dependencies()             │
│    └── pactl, ffmpeg present?       │
│                                     │
│    get_sources()                    │
│    └── pactl list short sources     │
│        └── Parse into inputs/monitors│
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 2. SOURCE SELECTION                 │
│    find_running_source(inputs)      │
│    find_running_source(monitors)    │
│                                     │
│    confirm_sources() loop           │
│    ├── display_sources_table()      │
│    └── Continue / Change input/monitor│
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 3. OUTPUT PATH                      │
│    if -o provided:                  │
│        use specified path           │
│    else:                            │
│        prompt_save_location()       │
│        └── default: recording_TIMESTAMP.ogg│
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 4. SINK CREATION                    │
│    create_combined_sink()           │
│    ├── pactl load-module null-sink  │
│    ├── pactl load-module loopback   │  (mic → sink)
│    └── pactl load-module loopback   │  (monitor → sink)
│                                     │
│    atexit.register(cleanup)         │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 5. RECORDING                        │
│    record_audio()                   │
│    ├── temp_path = /tmp/..._temp.ogg│
│    ├── start_recording(ffmpeg)      │
│    ├── signal.signal(SIGINT, handler)│
│    ├── process.wait()               │
│    │   └── Ctrl+C → write 'q' to stdin│
│    └── shutil.move(temp → final)    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 6. CLEANUP                          │
│    atexit.unregister(cleanup)       │
│    cleanup_combined_sink()          │
│    ├── unload monitor loopback      │
│    ├── unload input loopback        │
│    └── unload null sink             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 7. POST-RECORDING (optional)        │
│    if api_key configured:           │
│        prompt "Transcribe now?"     │
│        └── invoke run_process()     │
└─────────────────────────────────────┘
```

### Combined Sink Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PulseAudio Server                         │
│                                                              │
│  ┌─────────────┐                                            │
│  │  Microphone │                                            │
│  │   Source    │──┐                                         │
│  └─────────────┘  │  module-loopback                        │
│                   │  latency_msec=100                       │
│                   ▼                                         │
│              ┌────────────────────┐                         │
│              │   module-null-sink │                         │
│              │  "kakitori_combined"│                         │
│              │   48kHz, stereo     │                         │
│              └─────────┬──────────┘                         │
│                   ▲    │                                    │
│                   │    │ .monitor                           │
│  ┌─────────────┐  │    ▼                                    │
│  │   System    │──┘                                         │
│  │   Monitor   │  module-loopback          ┌──────────┐     │
│  └─────────────┘  latency_msec=100         │  ffmpeg  │◄────│
│                                            │ recording│     │
│                                            └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Modeling

### Key Entities

```python
@dataclass
class AudioSource:
    id: str       # PulseAudio numeric ID
    name: str     # Source name (e.g., "alsa_input.pci...")
    driver: str   # Driver name
    format: str   # Audio format specification
    state: str    # RUNNING, IDLE, SUSPENDED

@dataclass
class AvailableSources:
    inputs: list[AudioSource]    # microphones
    monitors: list[AudioSource]  # system audio monitors

@dataclass
class CombinedSink:
    sink_id: int              # null sink module ID
    input_loopback_id: int    # mic → sink loopback ID
    monitor_loopback_id: int  # system → sink loopback ID
    monitor_source: str       # combined output source name
```

### Entity Relationships

- `AvailableSources` aggregates `AudioSource` instances by type
- `CombinedSink` holds module IDs needed for cleanup (lifecycle token)
- Recording session consumes `CombinedSink.monitor_source` as input

## Key Decisions

### Decision 1: PulseAudio Null Sink for Audio Mixing

**Choice**: Mix audio at the PulseAudio server level using a null sink with loopbacks.

**Why**: Eliminates timestamp drift that occurs with dual-source ffmpeg mixing.

**Related**: [ADR-003](../architecture/ADR-003-pulseaudio-null-sink-mixing.md)

---

### Decision 2: Temp File Recording with Atomic Move

**Choice**: Record to `/tmp/` first, move to destination on success.

**Why**: Prevents partial files from appearing at user-specified location.

**Related**: [DES-002](../design/DES-002-atomic-file-operations.md)

---

### Decision 3: SIGINT Interception with ffmpeg 'q' Command

**Choice**: Write 'q' to ffmpeg stdin instead of letting SIGINT propagate.

**Why**: ffmpeg properly finalizes the file with correct headers and duration.

**Related**: [DES-003](../design/DES-003-ffmpeg-graceful-stop.md)

---

### Decision 4: Interactive Source Confirmation Loop

**Choice**: Display selected sources in a table, offer continue/change in a loop.

**Why**: Auto-selecting RUNNING sources provides good defaults; loop allows correction without forcing unnecessary interaction.

**Consequences**: Quick path for common case, flexible for edge cases.

---

### Decision 5: Layered Cleanup with atexit + try/finally

**Choice**: Register cleanup at sink creation, use try/finally for normal path, unregister on success.

**Why**: PulseAudio modules persist beyond process termination. Layered approach maximizes cleanup coverage.

**Related**: [DES-004](../design/DES-004-layered-cleanup.md)

---

### Decision 6: Opus Codec in OGG Container

**Choice**: Use libopus codec with .ogg extension for all recordings.

**Why**: Opus provides excellent quality at low bitrates, supports speech and music. OGG is a widely-supported open container format.

**Consequences**: Good compression for voice recordings, compatible with most media players.

## System Behavior

### Scenario: Successful Recording

```
Given: pactl and ffmpeg are installed, audio sources available
When: User runs `kakitori record`, confirms sources, presses Ctrl+C
Then: Recording saved to specified path, combined sink cleaned up
```

### Scenario: Missing Dependencies

```
Given: pactl is not installed
When: User runs `kakitori record`
Then: Error "Missing dependencies: pactl" with installation hint
```

### Scenario: No Input Sources

```
Given: No microphones detected
When: Record workflow starts
Then: Error "No input sources found", command exits
```

### Scenario: Sink Creation Failure

```
Given: PulseAudio module loading fails
When: Creating combined sink
Then: Error logged, partial modules cleaned up, command exits
```

### Scenario: Recording Interrupted

```
Given: Recording in progress
When: User presses Ctrl+C
Then: ffmpeg receives 'q', file finalized, moved to destination, sink cleaned up
```

## Notes

**Uncertainties:**

- Behavior when multiple Kakitori instances run simultaneously (sink name collision with "kakitori_combined")
- Cleanup reliability under SIGKILL (cannot be caught)

**Assumptions:**

- PulseAudio/PipeWire compatibility for module-null-sink and module-loopback
- `/tmp` has sufficient space for recording duration
- User has permissions to load/unload PulseAudio modules

**Future considerations:**

- Unique sink name per instance (include PID) for concurrent recordings
- Explicit handling of questionary returning None on Ctrl+C during prompts
