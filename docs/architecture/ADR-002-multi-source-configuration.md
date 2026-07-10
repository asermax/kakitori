# ADR-002: Multi-Source Configuration Merge

**Status**: Accepted
**Date**: 2026-01-01

## Context

Kakitori requires a Deepgram API key for transcription. Different users have different deployment scenarios:

- Personal use: Global API key shared across projects
- Per-project: Different keys for different contexts
- CI/CD: Environment variable injection
- Containers: Runtime configuration

We needed a configuration strategy that accommodates all these scenarios without complex setup.

## Decision

Load configuration from three sources using Python dictionary unpacking to implement priority order:

```python
return {
    **dotenv_values(CONFIG_DIR / ".env"),  # ~/.config/kakitori/.env (lowest)
    **dotenv_values(".env"),                # Local .env (middle)
    **os.environ,                           # Environment variables (highest)
}
```

Later sources override earlier ones due to dictionary key replacement.

## Consequences

### Positive

- Flexibility for different deployment scenarios
- Simple implementation using Python dict unpacking
- `dotenv_values()` returns empty dict for missing files (no error handling needed)
- Works out of the box for most users with a global key

### Negative

- Users may be confused about which source is active
- No way to display "resolved" configuration
- Debugging configuration issues requires checking three locations

## Alternatives Considered

### Single source only (environment variables)

- **Description**: Only read `DEEPGRAM_API_KEY` from environment
- **Why rejected**: Forces `export` on every session or permanent shell config changes

### Config file with sections (TOML/YAML)

- **Description**: Structured config file with explicit priority settings
- **Why rejected**: Overkill for a single key; adds parsing complexity

### Click's option chaining

- **Description**: Use Click's built-in config file support
- **Why rejected**: Ties to specific library; we use argparse

---

## Notes

- Retrofitted from existing implementation in CORE-001
- Error message in `_run_process_command` lists all three sources with setup instructions
- Related: [../feature-designs/CORE-001.md](../feature-designs/CORE-001.md)
