import os
import sys
from pathlib import Path

from dotenv import dotenv_values

from kakitori.cli import parse_args
from kakitori.logging import logger, setup_logging


CONFIG_DIR = Path.home() / ".config" / "kakitori"


def _load_config() -> dict:
    """Load configuration from multiple sources.

    Returns:
        Configuration dictionary with GEMINI_API_KEY
    """
    return {
        **dotenv_values(CONFIG_DIR / ".env"),
        **dotenv_values(".env"),
        **os.environ,
    }


def main() -> None:
    """Main entry point for kakitori CLI tool."""
    args = parse_args()
    setup_logging(args.verbose)

    if args.command == "record":
        _run_record_command(args)

    elif args.command == "process":
        _run_process_command(args)

    else:
        logger.error("No command specified. Use 'kakitori record' or 'kakitori process <file>'")
        sys.exit(1)


def _run_record_command(args) -> None:
    """Execute the record subcommand.

    Args:
        args: Parsed command-line arguments
    """
    from kakitori.record import run_record

    # Load config for optional transcription
    config = _load_config()
    api_key = config.get("GEMINI_API_KEY")

    try:
        result = run_record(args.output, api_key=api_key)

        if result is None:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.error("\nInterrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def _run_process_command(args) -> None:
    """Execute the process subcommand.

    Args:
        args: Parsed command-line arguments
    """
    config = _load_config()
    api_key = config.get("GEMINI_API_KEY")

    if api_key is None:
        logger.error("GEMINI_API_KEY not found")
        logger.error("\nSet it in one of these locations (in priority order):")
        logger.error("  1. System environment: export GEMINI_API_KEY=your-key")
        logger.error("  2. Local .env file in current directory")
        logger.error(f"  3. Global config: {CONFIG_DIR / '.env'}")
        logger.error("\nTo set up global config:")
        logger.error(f"  mkdir -p {CONFIG_DIR}")
        logger.error(f"  echo 'GEMINI_API_KEY=your-key' > {CONFIG_DIR / '.env'}")
        sys.exit(1)

    from kakitori.process import run_process

    try:
        run_process(
            audio_file=args.audio_file,
            api_key=api_key,
            output=args.output,
            stdout=args.stdout,
            skip_speaker_id=args.skip_speaker_id,
        )

    except KeyboardInterrupt:
        logger.error("\nInterrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
