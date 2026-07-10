# Design: CORE-001 - CLI Infrastructure

**Feature Spec**: [../feature-specs/CORE-001.md](../feature-specs/CORE-001.md)
**Status**: Approved

## Retrofit Note

This design was created from existing code at:
- `src/kakitori/__init__.py`
- `src/kakitori/cli.py`
- `src/kakitori/logging.py`

Original implementation date: Unknown (pre-framework)
Decisions documented during retrofit: ADR-001, ADR-002, DES-001

---

## Purpose

This document captures the design rationale inferred from the existing CLI infrastructure implementation.

## Problem Context

The CLI infrastructure solves the problem of providing a unified entry point for a tool that evolved from a single-purpose transcription utility to a multi-function recording and transcription system.

**Challenges addressed:**

1. **Multiple operations**: Users need both recording and transcription through a single tool
2. **Backwards compatibility**: Existing `kakitori <file>` invocations must continue working
3. **Configuration complexity**: API keys may come from multiple sources depending on user environment
4. **Clean output streams**: Transcripts need to be pipeable, requiring separation of logs from output
5. **Optional dependencies**: Recording and processing have different system requirements

**Constraints:**

- Python 3.11+ runtime
- Interactive terminal environment (questionary prompts)
- Unix-like platform (exit code conventions)

## Design Overview

The CLI follows a **layered dispatch pattern** with three distinct layers:

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Point                          │
│                   (__init__.py)                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  main()                                          │   │
│  │    ├── parse_args()  ─────────────────────────┐ │   │
│  │    ├── setup_logging()                        │ │   │
│  │    └── dispatch ─┬─> _run_record_command()    │ │   │
│  │                  └─> _run_process_command()   │ │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│   Argument      │ │   Logging   │ │  Configuration  │
│   Parsing       │ │   (logging. │ │  (_load_config) │
│   (cli.py)      │ │    py)      │ │                 │
└─────────────────┘ └─────────────┘ └─────────────────┘
```

**Separation of concerns:**

- `cli.py`: Pure argument parsing, no side effects
- `__init__.py`: Orchestration, configuration, dispatch
- `logging.py`: Logging configuration only

## Data Flow

### Execution Sequence

```
sys.argv
    │
    ▼
┌──────────────┐
│ parse_args() │  ◄── Subcommand detection or legacy fallback
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│ setup_logging()    │  ◄── Configure before any logging occurs
└──────────┬─────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Command Dispatch                      │
│   if command == "record":            │
│       _run_record_command(args)      │
│   elif command == "process":         │
│       _run_process_command(args)     │
└──────────────────────────────────────┘
           │
           ▼ (inside command handler)
┌──────────────────────────────────────┐
│ _load_config()                       │  ◄── Config loaded AFTER dispatch
│   global .env → local .env → os.env │
└──────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ API Key Validation                   │  ◄── Asymmetric: optional for record
│   record: optional (transcription)   │      required for process
│   process: required (exits with help)│
└──────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Interactive Prompts (if needed)      │  ◄── Participant count for process
└──────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Lazy Import Command Module           │  ◄── DES-001: defer dependencies
│   from kakitori.record import ...    │
│   from kakitori.process import ...   │
└──────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Execute Command                      │
│   Error boundary with exit codes     │
└──────────────────────────────────────┘
```

### Configuration Priority

```
┌─────────────────────────────────────────────────┐
│ Priority (highest to lowest)                     │
├─────────────────────────────────────────────────┤
│ 1. os.environ                    ──► HIGHEST    │
│    (system environment)                         │
│                                                 │
│ 2. .env (local)                                 │
│    (current directory)                          │
│                                                 │
│ 3. ~/.config/kakitori/.env       ──► LOWEST     │
│    (global config)                              │
└─────────────────────────────────────────────────┘

Implementation: Dictionary unpacking overwrites keys
    {**global, **local, **env}
```

## Modeling

### Key Entities

| Entity | Type | Role |
|--------|------|------|
| `args` | `argparse.Namespace` | Parsed CLI arguments with `command` discriminator |
| `config` | `dict` | Merged configuration from all sources |
| `logger` | `logging.Logger` | Application-wide logger to stderr |
| `CONFIG_DIR` | `Path` | Global config location `~/.config/kakitori` |

### Module Relationships

```
kakitori/
├── __init__.py          # Entry point, orchestration
│   ├── imports cli.parse_args
│   ├── imports logging.{logger, setup_logging}
│   └── lazy imports record/process commands
│
├── cli.py               # Pure argument parsing
│   └── no external dependencies
│
└── logging.py           # Logging configuration
    └── no external dependencies
```

## Key Decisions

### Decision 1: Subcommand Architecture with Legacy Fallback

**Choice**: Use argparse subparsers with re-parse fallback for backwards compatibility.

**Why**: Evolved from single-purpose tool; existing scripts use `kakitori <file>`.

**Trade-off**: Argument parsing happens twice for legacy invocations, but `_add_process_arguments()` is shared to reduce duplication.

**Related**: [ADR-001](../architecture/ADR-001-subcommand-architecture.md)

---

### Decision 2: Multi-Source Configuration with Dictionary Merge

**Choice**: Load config from global → local → env using dictionary unpacking.

**Why**: Different users have different preferences (global key vs per-project vs CI/CD).

**Related**: [ADR-002](../architecture/ADR-002-multi-source-configuration.md)

---

### Decision 3: Logging to stderr

**Choice**: All logs go to stderr with format `[LEVEL] message`.

**Why**: The `--stdout` flag outputs transcripts to stdout for piping. Logs must go elsewhere to avoid polluting the output stream.

**Consequences**: Clean stdout enables `kakitori process file.mp3 --stdout | other-tool`.

---

### Decision 4: Lazy Command Imports

**Choice**: Import command modules inside handler functions rather than at module level.

**Why**: Recording and processing have different dependencies. Lazy imports avoid loading unused code.

**Related**: [DES-001](../design/DES-001-lazy-command-imports.md)

---

### Decision 5: Asymmetric API Key Handling

**Choice**: Process command requires API key and exits with detailed help. Record command treats it as optional.

**Why**: Recording is valuable standalone; users may record now and transcribe later. Processing without transcription is pointless.

**Implementation**:
- `_run_record_command`: Loads config, passes `api_key` to `run_record()` as optional parameter
- `_run_process_command`: Checks for API key upfront, exits with actionable error message listing all configuration sources

---

### Decision 6: Actionable Error Messages

**Choice**: Error messages include setup instructions, not just error descriptions.

**Example**: Missing API key error shows all three configuration locations with setup commands.

**Why**: CLI users need guidance, not just failure notification. Reduces support burden.

## System Behavior

### Scenario: New User First Run (Process)

```
Given: No configuration exists
When: User runs `kakitori process meeting.mp3`
Then: Error shows all three config options with setup commands
```

### Scenario: Legacy Invocation

```
Given: User has scripts using `kakitori file.mp3`
When: Arguments are parsed
Then: Command set to "process", execution proceeds normally
```

### Scenario: Interrupted Recording

```
Given: User is recording audio
When: User presses Ctrl+C
Then: Exit code 130 (128 + SIGINT, Unix convention)
```

### Scenario: Global Config with Local Override

```
Given: ~/.config/kakitori/.env has DEEPGRAM_API_KEY=global-key
And: ./.env has DEEPGRAM_API_KEY=project-key
When: Configuration is loaded
Then: project-key is used (local overrides global)
```

## Notes

**Assumptions made during analysis:**

- Exit code 130 (128 + SIGINT) follows Unix convention intentionally
- The double-parse for legacy arguments is an acceptable performance trade-off
- Configuration loading happens per-command (not cached) intentionally
- `questionary.ask()` returning `None` on Ctrl+C is handled by the KeyboardInterrupt boundary

**XDG Compliance:**

- CONFIG_DIR uses `~/.config/kakitori` which aligns with XDG_CONFIG_HOME default
- Does not check XDG_CONFIG_HOME environment variable (could be enhanced)

**Verbose flag scope:**

- The `-v` flag is defined on the main parser, making it available globally
- Alternative would be per-subcommand verbosity (not implemented)
