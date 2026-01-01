# ADR-003: PulseAudio Null Sink for Audio Mixing

**Status**: Accepted
**Date**: 2026-01-01

## Context

Recording meetings requires capturing both microphone input (local speaker) and system audio (remote participants via video call). These are separate audio streams in PulseAudio/PipeWire that must be combined into a single recording.

The challenge is timestamp synchronization: when recording from two sources, each maintains its own clock. Over long recordings (30+ minutes), this leads to drift between the audio tracks.

## Decision

Create a temporary PulseAudio null sink with two loopback modules to mix audio at the audio server level:

```
┌─────────────────────────────────────────────────┐
│                 PulseAudio Server               │
│                                                 │
│  ┌───────────┐      ┌─────────────────────┐    │
│  │ Microphone│─────►│                     │    │
│  └───────────┘      │   module-null-sink  │    │
│                     │   "kakitori_combined"│───►│ Single stream
│  ┌───────────┐      │                     │    │ to ffmpeg
│  │ System    │─────►│                     │    │
│  │ Monitor   │      └─────────────────────┘    │
│  └───────────┘                                 │
└─────────────────────────────────────────────────┘
```

Implementation uses:
- `pactl load-module module-null-sink` - creates the mixing point
- `pactl load-module module-loopback` (x2) - routes each source to the sink

## Consequences

### Positive

- Reliable timestamp alignment regardless of recording duration
- Works with any PulseAudio/PipeWire compatible system
- No audio drift over long recordings
- Simple single-source ffmpeg command

### Negative

- Requires three pactl calls to set up
- Modules must be cleaned up (persist beyond process termination)
- Platform-specific (Linux with PulseAudio/PipeWire only)

## Alternatives Considered

### Dual-source ffmpeg mixing

- **Description**: Use ffmpeg's `-filter_complex amix` to combine two PulseAudio inputs
- **Why rejected**: Each source maintains independent timestamps, causing drift over long recordings

### Hardware mixer

- **Description**: Use physical audio mixer or sound card with multiple inputs
- **Why rejected**: Not universally available, requires specific hardware

### JACK audio system

- **Description**: Use JACK for low-latency audio routing
- **Why rejected**: More complex setup, not as widely available as PulseAudio

---

## Notes

- Retrofitted from RECORD-001 implementation
- Related: [DES-004 (Layered Cleanup)](../design/DES-004-layered-cleanup.md) for cleanup strategy
