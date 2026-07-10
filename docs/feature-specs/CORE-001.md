# CORE-001: CLI Infrastructure

## Retrofit Note

This spec was created from existing code at:
- `src/kakitori/__init__.py`
- `src/kakitori/cli.py`
- `src/kakitori/logging.py`

---

## User Story

As a user of the kakitori CLI tool,
I want a consistent command-line interface with subcommands for recording and processing audio,
So that I can easily invoke the appropriate functionality while maintaining backwards compatibility with previous versions.

## Behavior

The CLI infrastructure provides the entry point and orchestration layer for the kakitori tool:

1. **Argument Parsing**: Parses command-line arguments using a subcommand-based structure (`record`, `process`) while maintaining backwards compatibility for legacy `kakitori <file>` invocations.

2. **Configuration Loading**: Loads configuration from multiple sources with a defined priority order, merging them into a single configuration dictionary.

3. **Command Dispatch**: Routes execution to the appropriate command handler based on the parsed subcommand.

4. **Logging Setup**: Configures application-wide logging to stderr with configurable verbosity levels.

5. **Error Handling**: Provides consistent error handling and exit codes across all command paths.

## Acceptance Criteria

### Configuration Loading

- Given a global config file exists at `~/.config/kakitori/.env`
  When the tool is invoked
  Then configuration values are loaded from that file

- Given a local `.env` file exists in the current directory
  When the tool is invoked
  Then configuration values from the local file override global config values

- Given an environment variable is set (e.g., `DEEPGRAM_API_KEY`)
  When the tool is invoked
  Then the environment variable value takes highest priority over all file-based configs

- Given `DEEPGRAM_API_KEY` is not set in any configuration source
  When the `process` command is invoked
  Then an error message is displayed listing all configuration locations
  And the process exits with code 1

### Subcommand Parsing

- Given the user invokes `kakitori record`
  When arguments are parsed
  Then `args.command` equals "record"

- Given the user invokes `kakitori process <file>`
  When arguments are parsed
  Then `args.command` equals "process"
  And `args.audio_file` contains the file path

- Given the user invokes `kakitori record -o output.ogg`
  When arguments are parsed
  Then `args.output` equals "output.ogg"

- Given the user invokes `kakitori process file.mp3 --stdout`
  When arguments are parsed
  Then `args.stdout` is True

- Given the user invokes `kakitori process file.mp3 --skip-speaker-id`
  When arguments are parsed
  Then `args.skip_speaker_id` is True

### Backwards Compatibility

- Given the user invokes `kakitori <audio_file>` without a subcommand
  When arguments are parsed
  Then `args.command` is set to "process"
  And `args.audio_file` contains the file path

### File Validation

- Given an audio file path is provided that does not exist
  When the `process` command is parsed
  Then an error is displayed: "Audio file not found: <path>"
  And argument parsing fails

### Logging Setup

- Given the user invokes any command without `-v`
  When logging is configured
  Then the log level is set to INFO
  And logs are written to stderr

- Given the user invokes any command with `-v` or `--verbose`
  When logging is configured
  Then the log level is set to DEBUG
  And logs are written to stderr

- Given logging is configured
  When log messages are written
  Then they follow the format `[LEVEL] message`

### Error Handling

- Given any command execution is interrupted with Ctrl+C
  When the KeyboardInterrupt is caught
  Then the message "Interrupted by user" is logged
  And the process exits with code 130

- Given any command execution raises an exception
  When the exception is caught
  Then the error message is logged
  And the process exits with code 1

## Dependencies

### Python Dependencies

- `argparse` (standard library) - Command-line argument parsing
- `python-dotenv` - Loading .env files
- `questionary` - Interactive prompts (speaker identification, source selection)

## Technical Notes

### Configuration Priority

Priority order (highest to lowest):
1. System environment variables
2. Local `.env` file in current directory
3. Global config at `~/.config/kakitori/.env`

This allows users to have a single global API key while permitting per-project overrides.

### Exit Codes

- 0: Success
- 1: Error (missing config, exceptions)
- 130: Keyboard interrupt (128 + SIGINT, Unix convention)

### Lazy Imports

Command implementations (`run_record`, `run_process`) are imported lazily inside command handlers to avoid loading unnecessary dependencies.

### Logging to stderr

All logs go to stderr so that `--stdout` flag can output clean transcript to stdout for piping.
