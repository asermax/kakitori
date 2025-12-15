import time
from pathlib import Path

from google import genai
from google.genai import types

from kakitori.logging import logger
from kakitori.models import Transcription


TRANSCRIPTION_PROMPT = """
Transcribe this audio recording with detailed speaker diarization.

Requirements:
1. Identify each unique speaker and assign a consistent ID (Speaker 1, Speaker 2, etc.)
2. Include start timecode (MM:SS format) for each speech segment
3. Transcribe verbatim, preserving the original speech accurately
4. Ensure numerical values are transcribed precisely
5. Maintain consistency in speaker attribution throughout

Output the transcription in the specified JSON schema format.
""".strip()


def transcribe_audio(audio_path: str, api_key: str) -> tuple[Transcription, str]:
    """Transcribe an audio file using Gemini with speaker diarization.

    Args:
        audio_path: Path to the audio file
        api_key: Gemini API key

    Returns:
        Tuple of (Transcription object, file_name for cleanup)

    Raises:
        Exception: If file upload or transcription fails
    """
    client = genai.Client(api_key=api_key)

    # Determine MIME type from file extension
    path = Path(audio_path)
    mime_types = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
    }
    mime_type = mime_types.get(path.suffix.lower(), "audio/mpeg")

    logger.info(f"Uploading audio file: {audio_path}")
    logger.debug(f"MIME type: {mime_type}")

    audio_file = client.files.upload(
        file=audio_path,
        config=types.UploadFileConfig(
            display_name=path.name,
            mime_type=mime_type,
        ),
    )

    logger.debug(f"File uploaded: name={audio_file.name}, state={audio_file.state}")

    # Wait for processing to complete
    logger.info("Processing audio file...")

    while audio_file.state == "PROCESSING":
        time.sleep(2)
        audio_file = client.files.get(name=audio_file.name)
        logger.debug(f"File state: {audio_file.state}")

    if audio_file.state == "FAILED":
        raise Exception("Audio file processing failed")

    logger.debug("Audio file processed successfully")

    # Generate transcription with structured output
    logger.info("Generating transcription...")
    logger.debug("Model: gemini-flash-latest, temperature: 0.0, max_tokens: 65536")

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[audio_file, TRANSCRIPTION_PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Transcription,
            temperature=0.0,
            max_output_tokens=65536,
        ),
    )

    logger.debug(f"API response received: {response}")
    logger.debug(f"Response text: {response.text[:500] if response.text else 'None'}...")

    transcription = response.parsed

    if not transcription:
        raise Exception("Failed to parse transcription response")

    logger.info(f"Transcription complete: {len(transcription.segments)} segments")
    logger.debug(f"Segments: {[s.speaker for s in transcription.segments]}")

    return transcription, audio_file.name


def cleanup_file(api_key: str, file_name: str) -> None:
    """Delete an uploaded file from Gemini.

    Args:
        api_key: Gemini API key
        file_name: Name of the file to delete
    """
    client = genai.Client(api_key=api_key)
    client.files.delete(name=file_name)
