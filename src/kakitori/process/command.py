from pathlib import Path

from kakitori.logging import logger
from .output import format_transcript
from .speaker import apply_speaker_names, identify_speakers
from .transcribe import cleanup_file, transcribe_audio


def run_process(
    audio_file: str,
    api_key: str,
    output: str | None,
    stdout: bool,
    skip_speaker_id: bool,
) -> None:
    """Execute the transcription processing workflow.

    Args:
        audio_file: Path to audio file
        api_key: Gemini API key
        output: Custom output path or None
        stdout: Whether to print to stdout
        skip_speaker_id: Whether to skip speaker identification
    """
    # Step 1: Transcribe audio
    transcription, file_name = transcribe_audio(audio_file, api_key)

    # Step 2: Interactive speaker identification (unless skipped)
    if not skip_speaker_id:
        speaker_mapping = identify_speakers(transcription, audio_file)
        transcription = apply_speaker_names(transcription, speaker_mapping)

    else:
        logger.info("Skipping speaker identification")

    # Step 3: Format and output transcript
    formatted_output = format_transcript(transcription)

    if stdout:
        # Print to terminal
        print("\n" + "=" * 50)
        print("TRANSCRIPT")
        print("=" * 50)
        print(formatted_output)

    else:
        # Save to file (default or custom path)
        if output:
            output_path = Path(output)
        else:
            output_path = Path(audio_file).with_suffix(".txt")

        output_path.write_text(formatted_output, encoding="utf-8")
        logger.info(f"✓ Transcript saved to: {output_path}")

    # Step 4: Cleanup uploaded file
    cleanup_file(api_key, file_name)
    logger.info("✓ Cleanup complete")
