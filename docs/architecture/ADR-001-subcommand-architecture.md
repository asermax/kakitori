# ADR-001: Subcommand Architecture with Legacy Fallback

**Status**: Accepted
**Date**: 2026-01-01

## Context

Kakitori evolved from a single-purpose transcription tool (`kakitori <file>`) to a multi-function tool with recording and transcription capabilities. We needed a CLI structure that:

- Clearly separates recording and processing concerns
- Supports different argument sets for each command
- Maintains backwards compatibility with existing scripts using `kakitori <file>`

## Decision

Use argparse subparsers for `record` and `process` commands, with a fallback mechanism that re-parses arguments when no subcommand is detected.

```python
args = parser.parse_args()

if args.command is None:
    args = _parse_legacy_args()  # Re-parse with flat structure
```

The legacy parser treats the first positional argument as an audio file and implicitly sets `command = "process"`.

## Consequences

### Positive

- Zero breaking changes for existing users and scripts
- Clean separation of record vs process argument sets
- Clear, explicit command structure for new users

### Negative

- Argument parsing happens twice for legacy invocations
- `_add_process_arguments()` must be shared between two parsers
- Files named "record" or "process" could theoretically conflict (edge case)

## Alternatives Considered

### Breaking change - require subcommands

- **Description**: Remove legacy support, always require `kakitori record` or `kakitori process`
- **Why rejected**: Would break existing workflows and scripts

### Single parser with optional positional

- **Description**: Try to detect subcommand vs file in one parser
- **Why rejected**: Fragile, edge cases with files named "record"

### Click/Typer framework

- **Description**: Use a more sophisticated CLI framework
- **Why rejected**: Additional dependency, argparse is sufficient for our needs

---

## Notes

- Retrofitted from existing implementation in CORE-001
- Related: [../designs/CORE-001.md](../../designs/CORE-001.md)
