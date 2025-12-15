from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    """A single segment of transcribed audio with speaker and timestamp."""

    start_time: str
    speaker: str
    content: str


class Transcription(BaseModel):
    """Complete transcription with all segments."""

    segments: list[TranscriptSegment]
