import mpv


def parse_timestamp(timestamp: str) -> float:
    """Convert 'MM:SS' or 'HH:MM:SS' timestamp to seconds.

    Args:
        timestamp: Time in 'MM:SS' or 'HH:MM:SS' format

    Returns:
        Total seconds as float
    """
    parts = timestamp.split(":")

    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + int(seconds)

    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

    else:
        raise ValueError(f"Invalid timestamp format: {timestamp}")


def format_timestamp(seconds: float) -> str:
    """Convert seconds to 'MM:SS' or 'HH:MM:SS' timestamp format.

    Args:
        seconds: Total seconds

    Returns:
        Time formatted as 'MM:SS', or 'HH:MM:SS' if an hour or more
    """
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


def play_snippet(
    audio_path: str,
    start_seconds: float,
    duration: float = 5.0,
) -> None:
    """Play a snippet of audio from start_seconds for duration.

    Args:
        audio_path: Path to the audio file
        start_seconds: Starting position in seconds
        duration: Duration to play in seconds (default: 5.0)
    """
    player = mpv.MPV()

    try:
        player.start = start_seconds
        player.end = start_seconds + duration
        player.play(audio_path)
        player.wait_for_playback()
    finally:
        player.terminate()
