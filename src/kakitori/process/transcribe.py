import time
from pathlib import Path

from google import genai
from google.genai import types

from kakitori.logging import logger
from kakitori.models import Transcription


TRANSCRIPTION_PROMPT_TEMPLATE = """
Transcribe this audio recording with detailed speaker diarization.

Context:
- This recording has exactly {participant_count} participant(s)
- Transcribe approximately 20 minutes of audio per response
- If there is no more audio to transcribe, return an empty segments array

Requirements:
1. Identify each unique speaker with their actual name when possible:
   - Listen for names mentioned in conversation (e.g., "Hey John, what do you think?")
   - Listen for self-introductions (e.g., "I'm Sarah from...")
   - Once a name is detected, use it consistently for ALL that speaker's segments
   - Only use generic labels (Speaker 1, Speaker 2, etc.) when no name can be inferred
2. Include start timecode (MM:SS format) for each speech segment
3. Transcribe verbatim, preserving the original speech accurately
4. Ensure numerical values are transcribed precisely
5. Maintain consistency in speaker attribution throughout

Output the transcription in the specified JSON schema format.
""".strip()


CONTINUATION_PROMPT = """
Continue transcribing from where you left off.
If there is no more audio to transcribe, return an empty segments array.
""".strip()


def transcribe_audio(
    audio_path: str, api_key: str, participant_count: int
) -> tuple[Transcription, str]:
    """Transcribe an audio file using Gemini with speaker diarization.

    Args:
        audio_path: Path to the audio file
        api_key: Gemini API key
        participant_count: Number of participants in the recording

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

    # Generate transcription using multi-turn for long recordings
    logger.info("Starting multi-turn transcription...")
    logger.debug("Model: gemini-3-flash-preview, temperature: 0.3, max_tokens: 65536")

    # Create chat session with structured output config
    chat = client.chats.create(
        model="gemini-3-flash-preview",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Transcription,
            temperature=0.3,  # Low but non-zero to prevent repetition loops
            max_output_tokens=65536,
        ),
    )

    all_segments = []
    turn = 1

    # First turn with audio + initial prompt
    logger.info(f"Transcription turn {turn}...")
    initial_prompt = TRANSCRIPTION_PROMPT_TEMPLATE.format(participant_count=participant_count)
    response = chat.send_message([audio_file, initial_prompt])

    transcription = response.parsed
    if not transcription:
        # Get finish reason if available
        finish_reason = None
        if response.candidates:
            finish_reason = response.candidates[0].finish_reason

        raise Exception(
            f"Failed to parse transcription response (turn {turn})\n"
            f"Finish reason: {finish_reason}\n"
            f"Response text:\n{response.text}"
        )

    all_segments.extend(transcription.segments)
    logger.info(f"Turn {turn}: {len(transcription.segments)} segments")

    # Continue until empty array
    while transcription.segments:
        turn += 1
        logger.info(f"Transcription turn {turn}...")
        response = chat.send_message(CONTINUATION_PROMPT)

        transcription = response.parsed
        if not transcription:
            # Get finish reason if available
            finish_reason = None
            if response.candidates:
                finish_reason = response.candidates[0].finish_reason

            raise Exception(
                f"Failed to parse transcription response (turn {turn})\n"
                f"Finish reason: {finish_reason}\n"
                f"Response text:\n{response.text}"
            )

        if transcription.segments:
            all_segments.extend(transcription.segments)
            logger.info(f"Turn {turn}: {len(transcription.segments)} segments")
        else:
            logger.info(f"Turn {turn}: empty array, transcription complete")

    final_transcription = Transcription(segments=all_segments)
    logger.info(f"Transcription complete: {len(all_segments)} segments across {turn} turns")
    logger.debug(f"Speakers: {set(s.speaker for s in all_segments)}")

    return final_transcription, audio_file.name


def cleanup_file(api_key: str, file_name: str) -> None:
    """Delete an uploaded file from Gemini.

    Args:
        api_key: Gemini API key
        file_name: Name of the file to delete
    """
    client = genai.Client(api_key=api_key)
    client.files.delete(name=file_name)
