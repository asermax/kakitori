import os
import sys
from pathlib import Path

from dotenv import dotenv_values

from kakitori.cli import parse_args
from kakitori.logging import logger, setup_logging
from kakitori.output import format_transcript
from kakitori.speaker import apply_speaker_names, identify_speakers
from kakitori.transcribe import cleanup_file, transcribe_audio


CONFIG_DIR = Path.home() / ".config" / "kakitori"


def main() -> None:
    """Main entry point for kakitori CLI tool."""
    # Load configuration from multiple sources (priority: system env > local .env > global config)
    config = {
        **dotenv_values(CONFIG_DIR / ".env"),  # global config (lowest priority)
        **dotenv_values(".env"),                # local .env overrides global
        **os.environ,                           # system env has highest priority
    }

    # Parse command-line arguments
    args = parse_args()

    # Setup logging
    setup_logging(args.verbose)

    api_key = config.get("GEMINI_API_KEY")

    if not api_key:
        logger.error("GEMINI_API_KEY not found")
        logger.error("\nSet it in one of these locations (in priority order):")
        logger.error("  1. System environment: export GEMINI_API_KEY=your-key")
        logger.error("  2. Local .env file in current directory")
        logger.error(f"  3. Global config: {CONFIG_DIR / '.env'}")
        logger.error("\nTo set up global config:")
        logger.error(f"  mkdir -p {CONFIG_DIR}")
        logger.error(f"  echo 'GEMINI_API_KEY=your-key' > {CONFIG_DIR / '.env'}")
        sys.exit(1)

    try:
        # Step 1: Transcribe audio
        transcription, file_name = transcribe_audio(args.audio_file, api_key)

        # Step 2: Interactive speaker identification (unless skipped)
        if not args.skip_speaker_id:
            speaker_mapping = identify_speakers(transcription, args.audio_file)
            transcription = apply_speaker_names(transcription, speaker_mapping)

        else:
            logger.info("Skipping speaker identification")

        # Step 3: Format and output transcript
        formatted_output = format_transcript(transcription)

        if args.stdout:
            # Print to terminal
            print("\n" + "=" * 50)
            print("TRANSCRIPT")
            print("=" * 50)
            print(formatted_output)

        else:
            # Save to file (default or custom path)
            if args.output:
                output_path = Path(args.output)
            else:
                output_path = Path(args.audio_file).with_suffix(".txt")

            output_path.write_text(formatted_output, encoding="utf-8")
            logger.info(f"✓ Transcript saved to: {output_path}")

        # Step 4: Cleanup uploaded file
        cleanup_file(api_key, file_name)
        logger.info("✓ Cleanup complete")

    except KeyboardInterrupt:
        logger.error("\nInterrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
