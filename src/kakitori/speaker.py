from kakitori.audio import parse_timestamp, play_snippet
from kakitori.logging import logger
from kakitori.models import Transcription, TranscriptSegment


def get_snippet_duration(
    segments: list[TranscriptSegment],
    current_index: int,
    max_duration: float = 5.0,
) -> float:
    """Calculate snippet duration based on next segment, capped at max_duration.

    Args:
        segments: Full list of all transcript segments
        current_index: Index of the current segment
        max_duration: Maximum duration in seconds (default: 5.0)

    Returns:
        Duration in seconds, limited by next segment or max_duration
    """
    current_start = parse_timestamp(segments[current_index].start_time)

    # If there's a next segment, use its start time as the boundary
    if current_index + 1 < len(segments):
        next_start = parse_timestamp(segments[current_index + 1].start_time)
        actual_duration = next_start - current_start
        calculated_duration = min(actual_duration, max_duration)

        logger.debug(
            f"Snippet duration: current_start={current_start:.2f}s, next_start={next_start:.2f}s, "
            f"actual={actual_duration:.2f}s, using={calculated_duration:.2f}s"
        )

        return calculated_duration

    logger.debug(f"Snippet duration: using max_duration={max_duration}s (last segment)")
    return max_duration


def identify_speakers(
    transcription: Transcription,
    audio_path: str,
) -> dict[str, str]:
    """Interactively identify speakers by playing audio snippets.

    Args:
        transcription: Transcription with generic speaker labels
        audio_path: Path to the audio file

    Returns:
        Dictionary mapping generic speaker labels to assigned names
    """
    # Extract unique speakers
    unique_speakers = sorted(
        set(segment.speaker for segment in transcription.segments)
    )

    logger.info(f"Found {len(unique_speakers)} speakers to identify")
    logger.debug(f"Unique speakers: {unique_speakers}")
    print("=" * 50)

    speaker_mapping = {}

    for speaker in unique_speakers:
        logger.info(f"Identifying {speaker}")
        print(f"\n{speaker}:")
        print("-" * 50)

        # Find segments for this speaker (up to 3-5) with their indices
        speaker_segment_indices = [
            idx
            for idx, segment in enumerate(transcription.segments)
            if segment.speaker == speaker
        ][:5]

        # Play snippets and get user input
        while True:
            logger.debug(f"Playing {len(speaker_segment_indices)} snippet(s) for {speaker}")
            print(f"\nPlaying {len(speaker_segment_indices)} snippet(s) for {speaker}...")

            for i, segment_idx in enumerate(speaker_segment_indices, 1):
                segment = transcription.segments[segment_idx]
                print(f"\nSnippet {i}/{len(speaker_segment_indices)}: [{segment.start_time}]")
                print(f"  \"{segment.content[:80]}...\"" if len(segment.content) > 80 else f"  \"{segment.content}\"")

                start_seconds = parse_timestamp(segment.start_time)
                duration = get_snippet_duration(
                    transcription.segments,
                    segment_idx,
                    max_duration=5.0,
                )

                logger.debug(f"Playing snippet {i}: start={start_seconds:.2f}s, duration={duration:.2f}s")
                play_snippet(audio_path, start_seconds, duration=duration)

            # Get user input
            name = input(f"\nWho is {speaker}? (press Enter to replay, or type name): ").strip()

            if name:
                speaker_mapping[speaker] = name
                logger.info(f"✓ {speaker} identified as: {name}")
                print(f"✓ {speaker} identified as: {name}")
                break

            else:
                logger.debug("User requested replay")
                print("Replaying...")

    return speaker_mapping


def apply_speaker_names(
    transcription: Transcription,
    speaker_mapping: dict[str, str],
) -> Transcription:
    """Apply speaker names to transcription segments.

    Args:
        transcription: Original transcription with generic labels
        speaker_mapping: Dictionary mapping generic labels to names

    Returns:
        Updated transcription with speaker names
    """
    for segment in transcription.segments:
        if segment.speaker in speaker_mapping:
            segment.speaker = speaker_mapping[segment.speaker]

    return transcription
