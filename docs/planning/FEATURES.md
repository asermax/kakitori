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

### CORE-002: Migrate CLI from argparse to cyclopts
**Status**: ✓ Defined
**Complexity**: Easy
**Description**: Replace argparse-based CLI with cyclopts for type-hint-driven argument parsing. Support two subcommands: `record` (with -o/--output, -v/--verbose) and `process` (with audio_file, -o/--output, --stdout, --skip-speaker-id, -p/--participants, -v/--verbose). Remove backwards compatibility for `kakitori <file>` syntax. Follows hayamimi pattern with `App` and `Annotated[Type, Parameter(...)]`.

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

### PROCESS-002: Multi-LLM Provider Support via llm Library
**Status**: ✓ Design
**Complexity**: Hard
**Description**: Replace direct Gemini API integration with Simon Willison's llm library to support multiple LLM providers (OpenAI, Anthropic, etc.) while defaulting to Gemini. Includes provider-specific file upload handling and graceful feature degradation for providers that don't support audio natively or structured outputs.

---

## Feature Count Summary

- **CORE**: 2 features (1 medium, 1 easy)
- **RECORD**: 1 feature (1 hard)
- **PROCESS**: 2 features (2 hard)

**Total**: 5 features
- Easy: 1
- Medium: 1
- Hard: 3

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
