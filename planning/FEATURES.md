# Feature Inventory

Atomic features extracted from VISION.md for the Kakitori audio recording and transcription tool.

## Feature Categories

1. **CORE** - CLI infrastructure, configuration, logging
2. **RECORD** - Audio recording with source mixing
3. **PROCESS** - Transcription and speaker identification

## Status Tracking

Features track their progress through the development workflow using a status field:

- **✓ Defined** - Feature extracted and documented (initial state)
- **⧗ Spec** - Specification in progress (`/spec-feature` started)
- **✓ Spec** - Specification complete (`/spec-feature` done)
- **⧗ Design** - Design rationale in progress (`/design-feature` started)
- **✓ Design** - Design complete (`/design-feature` done)
- **⧗ Plan** - Implementation plan in progress (`/plan-feature` started)
- **✓ Plan** - Implementation plan complete (`/plan-feature` done)
- **⧗ Implementation** - Feature implementation in progress (`/implement-feature` started)
- **✓ Implementation** - Feature complete and tested (`/implement-feature` done)

Commands automatically update status as they progress. To manually update:
```bash
python scripts/features.py status set FEATURE-ID "STATUS"
```

Query status:
```bash
python scripts/features.py status list                    # All features
python scripts/features.py status list --phase 1          # Filter by phase
python scripts/features.py status list --category CORE    # Filter by category
python scripts/features.py status show FEATURE-ID         # Detailed view
```

---

## CORE - CLI Infrastructure

### CORE-001: CLI Infrastructure
**Status**: ✓ Implementation
**Complexity**: Medium
**Description**: Subcommand-based CLI with configuration loading, logging setup, and backwards compatibility

---

## RECORD - Audio Recording

### RECORD-001: Audio Recording with Combined Sources
**Status**: ✓ Implementation
**Complexity**: Hard
**Description**: Capture microphone and system audio into a single recording using PulseAudio combined sink

---

## PROCESS - Transcription

### PROCESS-001: Audio Transcription Processing
**Status**: ✓ Implementation
**Complexity**: Hard
**Description**: Transcribe audio with speaker diarization using Gemini, with interactive speaker identification and multi-turn processing

---

## Feature Count Summary

- **CORE**: 1 feature (1 medium)
- **RECORD**: 1 feature (1 hard)
- **PROCESS**: 1 feature (1 hard)

**Total**: 3 features
- Easy: 0
- Medium: 1
- Hard: 2

---

## Atomicity Check

For each feature:
- ✓ Can be implemented in a single focused session
- ✓ Does ONE thing
- ✓ Has clear acceptance criteria
- ✓ Can be tested independently

If any feature fails these checks, split it into smaller features.

---

## Notes

- RECORD-001 can optionally invoke PROCESS-001 after recording (soft dependency)
- Both RECORD-001 and PROCESS-001 depend on CORE-001 for CLI infrastructure
- All features are currently implemented and complete
