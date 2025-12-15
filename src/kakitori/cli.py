import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="kakitori",
        description="Audio transcription with speaker diarization using Gemini",
    )

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

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Validate audio file exists
    if not Path(args.audio_file).exists():
        parser.error(f"Audio file not found: {args.audio_file}")

    return args
