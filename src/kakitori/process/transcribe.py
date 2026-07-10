from pathlib import Path

from deepgram import DeepgramClient

from kakitori.logging import logger
from kakitori.models import Transcription, TranscriptSegment
from .audio import format_timestamp

REQUEST_TIMEOUT_SECONDS = 1800.0  # generous ceiling for ~2hr recordings in a single request


def transcribe_audio(audio_path: str, api_key: str) -> Transcription:
    """Transcribe an audio file using Deepgram nova-3 with speaker diarization.

    Args:
        audio_path: Path to the audio file
        api_key: Deepgram API key

    Returns:
        Transcription object with segments ordered chronologically

    Raises:
        Exception: If transcription fails
    """
    client = DeepgramClient(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS)

    logger.info(f"Transcribing audio file: {audio_path}")
    logger.debug("Model: nova-3, diarize: True, utterances: True")

    with Path(audio_path).open("rb") as audio_file:
        response = client.listen.v1.media.transcribe_file(
            request=audio_file.read(),
            model="nova-3",
            diarize=True,
            utterances=True,
            punctuate=True,
            detect_language=True,
        )

    utterances = response.results.utterances or []
    segments = [
        TranscriptSegment(
            start_time=format_timestamp(utterance.start or 0.0),
            speaker=f"Speaker {(utterance.speaker or 0) + 1}",
            content=utterance.transcript or "",
        )
        for utterance in utterances
    ]

    channels = response.results.channels
    language = (channels[0].detected_language if channels else None) or "unknown"

    logger.info(f"Transcription complete: {len(segments)} segments, language: {language}")
    logger.debug(f"Speakers: {sorted(set(s.speaker for s in segments))}")

    return Transcription(segments=segments)
