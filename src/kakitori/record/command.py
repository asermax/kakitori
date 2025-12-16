from datetime import datetime
from pathlib import Path

import questionary

from kakitori.logging import logger
from kakitori.record.recorder import record_audio
from kakitori.record.sources import check_dependencies, find_running_source, get_sources
from kakitori.record.ui import confirm_sources, prompt_save_location


def run_record(output: str | None, api_key: str | None = None) -> Path | None:
    """Execute the recording workflow.

    Args:
        output: Custom output path or None (will prompt)
        api_key: Gemini API key for optional transcription

    Returns:
        Path to recorded file if successful, None otherwise
    """
    # Check dependencies first
    missing = check_dependencies()

    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error("Install with: sudo pacman -S pulseaudio-utils ffmpeg")
        return None

    # Get available sources
    try:
        sources = get_sources()
    except RuntimeError as e:
        logger.error(f"Failed to get audio sources: {e}")
        return None

    if not sources.inputs:
        logger.error("No input sources found")
        return None

    if not sources.monitors:
        logger.error("No monitor sources found")
        return None

    # Auto-select running sources
    input_source = find_running_source(sources.inputs)
    monitor_source = find_running_source(sources.monitors)

    # Interactive confirmation/selection
    input_source, monitor_source = confirm_sources(
        sources,
        input_source,
        monitor_source,
    )

    # User cancelled
    if input_source is None or monitor_source is None:
        logger.info("Recording cancelled")
        return None

    # Determine output path
    if output is not None:
        output_path = Path(output)

        if not output_path.suffix:
            output_path = output_path.with_suffix(".ogg")

    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = prompt_save_location(f"recording_{timestamp}.ogg")

        if output_path is None:
            logger.info("Recording cancelled")
            return None

    # Execute recording
    logger.info("Starting recording... Press Ctrl+C to stop.")

    success = record_audio(
        input_source.name,
        monitor_source.name,
        output_path,
    )

    if not success:
        logger.error("Recording failed")
        return None

    logger.info(f"✓ Recording saved to: {output_path}")

    # Prompt to transcribe
    if api_key is not None:
        should_transcribe = questionary.confirm(
            "Transcribe the recording now?",
            default=False,
        ).ask()

        if should_transcribe:
            from kakitori.process import run_process

            logger.info("\nStarting transcription...")

            run_process(
                audio_file=str(output_path),
                api_key=api_key,
                output=None,
                stdout=False,
                skip_speaker_id=False,
            )

    return output_path
