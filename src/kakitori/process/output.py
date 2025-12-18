from kakitori.models import Transcription


def format_transcript(transcription: Transcription) -> str:
    """Format transcription as plain text with timestamps and speakers.

    Args:
        transcription: Transcription object to format

    Returns:
        Formatted plain text string
    """
    lines = []

    for segment in transcription.segments:
        lines.append(f"[{segment.start_time}] {segment.speaker}: {segment.content}")

    return "\n".join(lines)
