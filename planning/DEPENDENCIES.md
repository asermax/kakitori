# Dependency Matrix

Features listed in rows depend on features in columns.
Mark with `X` where row depends on column.

## Full Dependency Matrix

|              | C001 | R001 | P001 |
|--------------|------|------|------|
| CORE-001     | -    |      |      |
| RECORD-001   | X    | -    |      |
| PROCESS-001  | X    |      | -    |

**Legend:**
- C001: CORE-001
- R001: RECORD-001
- P001: PROCESS-001

---

## Implementation Phases (derived from matrix)

### Phase 1: Core Infrastructure (1 feature)

Foundation features with no dependencies:
- **CORE-001**: CLI Infrastructure (subcommand parsing, configuration loading, logging setup)

**Test Milestone**: "CLI parses subcommands correctly, loads configuration from multiple sources, logging works with verbose flag."

### Phase 2: Commands (2 features)

Features that depend on Phase 1:
- **RECORD-001**: Audio Recording with Combined Sources (depends: CORE-001)
- **PROCESS-001**: Audio Transcription Processing (depends: CORE-001)

**Test Milestone**: "Record command captures microphone and system audio. Process command transcribes audio with speaker diarization."

---

## Dependency Notes

### Key Decisions

1. **Independent commands**: RECORD-001 and PROCESS-001 are independent of each other. Recording can optionally invoke processing afterward (soft dependency, not modeled).

2. **Shared infrastructure**: Both commands depend on CORE-001 for CLI parsing, configuration loading, and logging.

### Implementation Notes

- **Phase 1** is sequential: single feature
- **Phase 2** can be parallelized: RECORD-001 and PROCESS-001 are independent
