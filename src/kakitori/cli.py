import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments with subcommand support.

    Returns:
        Parsed arguments namespace with 'command' attribute
    """
    parser = argparse.ArgumentParser(
        prog="kakitori",
        description="Audio transcription with speaker diarization using Deepgram",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        metavar="<command>",
    )

    # Record subcommand
    record_parser = subparsers.add_parser(
        "record",
        help="Record audio from microphone and system audio",
    )

    record_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file path (default: prompts for filename)",
    )

    # Process subcommand
    process_parser = subparsers.add_parser(
        "process",
        help="Process and transcribe an existing audio file",
    )

    _add_process_arguments(process_parser)

    args = parser.parse_args()

    # Handle backwards compatibility: bare audio file argument
    if args.command is None:
        args = _parse_legacy_args()

    # Validate audio file exists for process command
    if args.command == "process" and not Path(args.audio_file).exists():
        parser.error(f"Audio file not found: {args.audio_file}")

    return args


def _add_process_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the process subcommand.

    Args:
        parser: Parser to add arguments to
    """
    parser.add_argument(
        "audio_file",
        type=str,
        help="Path to the audio file to transcribe",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file path (default: same name as audio file with .txt extension)",
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print transcript to stdout instead of saving to file",
    )

    parser.add_argument(
        "--skip-speaker-id",
        action="store_true",
        help="Skip interactive speaker identification (keep generic labels)",
    )


def _parse_legacy_args() -> argparse.Namespace:
    """Parse arguments for backwards compatibility (no subcommand).

    Handles: kakitori <audio_file> [options]

    Returns:
        Parsed arguments with command set to "process"
    """
    parser = argparse.ArgumentParser(
        prog="kakitori",
        description="Audio transcription with speaker diarization using Deepgram",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    _add_process_arguments(parser)

    args = parser.parse_args()
    args.command = "process"  # Set command to process for legacy invocation

    return args
