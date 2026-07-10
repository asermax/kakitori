# PROCESS-002: Multi-LLM Provider Support

## Status Note (2026-07-10): Superseded, Not Implemented

This feature was never implemented. Before it was picked up, the project decided to drop Gemini altogether and migrate the transcription backend directly to Deepgram's nova-3 model (single synchronous `client.listen.v1.media.transcribe_file(...)` call with `diarize=True`, `utterances=True`) instead of building the Gemini/OpenAI multi-provider abstraction described below. There is no provider abstraction layer, no `llm`/`llm-gemini` dependency, and no OpenAI transcription support in the codebase — `deepgram-sdk` is the sole transcription dependency, configured via `DEEPGRAM_API_KEY`.

The rest of this document is preserved as-is for historical reference; it describes a design that was never built and does not reflect the current codebase.

## User Story

As a kakitori user,
I want to use different LLM providers (Google Gemini, OpenAI) for audio transcription,
So that I can choose the best provider based on cost, performance, availability, or personal preference.

## What It Does

This feature replaces the direct Gemini API integration with a provider abstraction layer. Gemini support uses the `llm` library with the `llm-gemini` plugin for unified interface. OpenAI support uses the `openai` SDK directly to access the `gpt-4o-transcribe-diarize` model (since llm library doesn't support the transcription endpoint). Users configure their provider choice via `KAKITORI_PROVIDER` and `KAKITORI_PROVIDER_KEY` environment variables. OpenAI dependencies are optional extras.

## Acceptance Criteria

### Provider Selection and Configuration

- Given the user has not set `KAKITORI_PROVIDER`
  When the process command runs
  Then the system defaults to Gemini (`gemini-3-flash-preview` model)

- Given the user sets `KAKITORI_PROVIDER=gemini`
  When the process command runs
  Then the system uses llm library with llm-gemini plugin for transcription
  And reads the API key from `KAKITORI_PROVIDER_KEY`
  And configures the llm library programmatically with the API key

- Given the user sets `KAKITORI_PROVIDER=openai`
  When the process command runs
  Then the system uses OpenAI SDK with `gpt-4o-transcribe-diarize` model for transcription
  And reads the API key from `KAKITORI_PROVIDER_KEY`

- Given the user sets `KAKITORI_PROVIDER` to an unsupported provider
  When the process command runs
  Then an error message is displayed listing supported providers (gemini, openai)

### Gemini Provider Implementation (via llm library)

- Given the user selects Gemini provider
  When transcribing an audio file
  Then the system uses `llm.get_model("gemini-3-flash-preview")`
  And creates an attachment using `llm.Attachment.from_file(audio_path)`
  And uses multi-turn conversation with `model.conversation()`
  And passes the Transcription Pydantic model as schema parameter
  And parses response with `json.loads(response.text())`
  And validates against Transcription schema with Pydantic
  And the result is a Transcription object with speaker-diarized segments

- Given a long audio recording with Gemini provider
  When transcription is performed
  Then the system uses multi-turn conversation approach (existing implementation pattern)
  And sends continuation prompts until receiving empty segments array
  And combines all segments into a single Transcription object

### OpenAI Provider Implementation (via openai SDK)

- Given the user selects OpenAI provider
  When transcribing an audio file
  Then the system uses `openai.audio.transcriptions.create()`
  And specifies model `gpt-4o-transcribe-diarize`
  And specifies `response_format="diarized_json"`
  And specifies `chunking_strategy="auto"`
  And parses the response into Transcription schema format
  And the result matches the same Transcription format as Gemini

- Given the OpenAI response contains speaker segments
  When parsing the response
  Then each segment's speaker label (A, B, C...) is mapped consistently to Speaker 1, Speaker 2, etc.
  And the mapping preserves order of first appearance (A → Speaker 1, B → Speaker 2, etc.)
  And timestamps (in seconds) are converted to HH:MM:SS format for recordings >= 60 minutes
  And timestamps (in seconds) are converted to MM:SS format for recordings < 60 minutes
  And segments are converted to TranscriptSegment objects

- Given the OpenAI response has diarized_json structure
  When parsing the response
  Then the response must contain a `segments` array
  And each segment must have `speaker`, `text`, `start`, and `end` fields
  And optional fields (`id`, `type`) are validated if present but not required
  And the root level `duration` and `task` fields are validated but not stored

### Optional Dependencies

- Given the user has not installed openai extras
  When selecting `KAKITORI_PROVIDER=openai`
  Then an error message is displayed: "OpenAI provider requires optional dependencies. Install with: uv pip install kakitori[openai]"
  And the program exits with error code

- Given the user has installed with `kakitori[openai]`
  When selecting `KAKITORI_PROVIDER=openai`
  Then the openai SDK is available and transcription proceeds normally

### Provider-Specific Prompt Templates

- Given the user selects Gemini provider
  When generating transcription prompts
  Then the system uses Gemini-optimized prompt template with multi-turn instructions

- Given the user selects OpenAI provider
  When generating transcription requests
  Then the system uses OpenAI-specific parameters (chunking_strategy, participant hints via prompt)

- Given any provider
  When no provider-specific template exists
  Then a default prompt template is used as fallback

### API Key Management

- Given the user sets `KAKITORI_PROVIDER_KEY` environment variable
  When the process command runs
  Then the system uses this key for the selected provider

- Given the user has not set `KAKITORI_PROVIDER_KEY`
  When the process command runs
  Then an error message is displayed: "API key required. Set KAKITORI_PROVIDER_KEY environment variable."
  And the program exits with error code 1

- Given the user provides an invalid API key
  When the provider API returns a 401 authentication error
  Then an error message is displayed: "Invalid API key for {provider}. Check your KAKITORI_PROVIDER_KEY."
  And the program exits with error code 1

### Edge Cases

- Given the audio file does not exist
  When transcription is attempted
  Then an error message is displayed: "Audio file not found: {path}"
  And the program exits with error code 1

- Given the audio file exists but is not readable
  When transcription is attempted
  Then an error message is displayed: "Cannot read audio file: {path}. Check permissions."
  And the program exits with error code 1

- Given an empty audio file (0 seconds duration)
  When transcription is attempted
  Then an error message is displayed: "Audio file is empty or has 0 duration."
  And the program exits with error code 1

- Given participant_count is 0 or negative
  When transcription is attempted
  Then an error message is displayed: "Participant count must be positive (got {participant_count})"
  And the program exits with error code 1

- Given an audio file with only silence or noise (no speech)
  When transcription is attempted
  Then the provider processes it normally
  And returns an empty segments array or minimal/unclear transcription

- Given a very short audio file (< 1 second)
  When transcription is attempted
  Then the provider processes it normally
  And returns whatever transcript is possible (may be empty)

- Given an audio file in an unsupported format
  When the provider API rejects the format
  Then an error message is displayed: "Unsupported audio format for {provider}. Supported: {formats}"
  And the program exits with error code 1

- Given the provider API returns a rate limit error
  When transcription is attempted
  Then an error message is displayed: "{Provider} rate limit exceeded. Try again later."
  And the program exits with error code 1

- Given a network timeout during transcription
  When the provider API call times out
  Then an error message is displayed: "Network timeout while transcribing with {provider}."
  And the program exits with error code 1

- Given OpenAI returns non-consecutive speaker labels (A, B, E - skipping C, D)
  When parsing the response
  Then speaker labels are mapped in order of appearance
  And the mapping algorithm handles gaps transparently (A→Speaker 1, B→Speaker 2, E→Speaker 3)

- Given the detected speaker count differs from participant_count
  When transcription completes
  Then a warning is logged: "Detected {detected} speakers but expected {participant_count}"
  And transcription proceeds with actual detected speakers

- Given a very long audio file requiring many turns (Gemini)
  When multi-turn transcription is performed
  Then the system continues for up to 100 turns
  And if 100 turns is exceeded, an error is raised: "Transcription exceeded maximum turns (100)"

- Given the llm library returns a response without expected schema format
  When parsing the Gemini response
  Then the system validates against the Transcription Pydantic model
  And if validation fails, an error is displayed with validation details

### Error Cases

- Given the openai package is not installed
  When the user selects `KAKITORI_PROVIDER=openai`
  Then an error message is displayed: "OpenAI provider requires optional dependencies. Install with: uv pip install kakitori[openai]"
  And the program exits with error code 1

- Given the llm-gemini plugin is not installed
  When loading the Gemini model with `llm.get_model("gemini-3-flash-preview")`
  Then an error is raised by the llm library
  And an error message is displayed: "Gemini model not available. Install llm-gemini: uv pip install llm-gemini>=0.28"
  And the program exits with error code 1

- Given the specified Gemini model is not available
  When calling `llm.get_model("gemini-3-flash-preview")`
  Then an error is raised by the llm library with available models
  And the error is displayed to the user
  And the program exits with error code 1

- Given the provider API returns an error during transcription
  When processing the audio
  Then the error is caught and displayed with provider-specific context
  And the program exits with error code

- Given OpenAI returns a response without expected diarized_json structure
  When parsing the transcription
  Then an error message is displayed with the raw response for debugging
  And the program exits with error code

- Given a provider's response cannot be parsed into the Transcription schema
  When validating the parsed data
  Then an error message is displayed with validation errors
  And the program exits with error code

## Requires

Dependencies:
- PROCESS-001 (Audio Transcription Processing) - This feature refactors the transcription implementation

---

## Notes

### Provider Capability Matrix

| Provider | Audio Support | Diarization | SDK | Optional |
|----------|---------------|-------------|-----|----------|
| Gemini | ✓ Native | ✓ Built-in | `llm` + `llm-gemini` | No (core) |
| OpenAI | ✓ Native | ✓ gpt-4o-transcribe-diarize | `openai` | Yes |

**OpenAI speaker limit**: Supports up to 4 speakers. Recordings with more speakers may have reduced diarization accuracy.

### OpenAI Response Format

The `diarized_json` response structure:
```json
{
  "segments": [
    {"speaker": "A", "text": "Hello", "start": 0.5, "end": 3.2},
    {"speaker": "B", "text": "Hi there", "start": 3.5, "end": 5.8}
  ]
}
```

Speaker labels (A, B, C...) are mapped to "Speaker 1", "Speaker 2", etc. in order of first appearance.

### Configuration

Environment variables:
- `KAKITORI_PROVIDER` - Provider selection (default: "gemini")
- `KAKITORI_PROVIDER_KEY` - API key for selected provider (required)

No fallbacks - users must update to new environment variable names.

### Dependencies

**Core** (required):
- `llm>=0.17` - LLM library with schema support
- `llm-gemini>=0.28` - Gemini 3 Flash support (replaces `google-genai`)

**Optional** (extras):
- `openai>=1.60.0` - OpenAI transcription support

**Installation**:
```bash
# Gemini only (default)
uv tool install kakitori

# With OpenAI support
uv tool install 'kakitori[openai]'
```

**Removed**: `google-genai` (replaced by llm + llm-gemini)

### Supported Audio Formats

**Gemini** (via llm-gemini):
- MP3 (audio/mpeg)
- WAV (audio/wav)
- M4A (audio/mp4)
- OGG (audio/ogg)
- FLAC (audio/flac)

**OpenAI** (gpt-4o-transcribe-diarize):
- FLAC
- MP3
- MP4
- MPEG
- MPGA
- M4A
- OGG
- WAV
- WebM

**File size limits**:
- Gemini: No explicit limit (uses Files API with upload)
- OpenAI: ~25MB per file (chunking_strategy=auto handles internally)

### Configuration Files

Update `~/.config/kakitori/.env` or local `.env`:
```bash
# Provider selection
KAKITORI_PROVIDER=gemini  # or openai

# API key (single key for selected provider)
KAKITORI_PROVIDER_KEY=your-api-key-here
```

### Migration Notes

**Breaking changes**:
- Removes `google-genai` dependency (replaced by `llm` + `llm-gemini`)
- Changes from `GEMINI_API_KEY` to `KAKITORI_PROVIDER_KEY` (no fallback)
- Changes from `gemini-flash-latest` to `gemini-3-flash-preview` model
- No manual file cleanup needed (llm-gemini handles with 48hr TTL)

**Users must**:
1. Update environment variable: `KAKITORI_PROVIDER_KEY=<your-key>`
2. Optionally set `KAKITORI_PROVIDER=gemini` (default) or `openai`
3. For OpenAI: Install with `uv tool install 'kakitori[openai]'`
4. CLI interface remains the same - no command changes needed

### Future Provider Support

Potential providers to add later (all would be optional extras):
- **AssemblyAI** - Excellent speaker diarization
- **Azure Speech Services** - Enterprise-grade
- **Deepgram** - Real-time transcription

### Research Sources

- [llm library schema support](https://simonwillison.net/2025/Feb/28/llm-schemas/) - Pydantic model integration
- [Gemini 3 Flash announcement](https://blog.google/products/gemini/gemini-3-flash/) - Model capabilities
- [llm-gemini releases](https://github.com/simonw/llm-gemini/releases) - Plugin version requirements
- [OpenAI Audio Transcription API](https://platform.openai.com/docs/guides/speech-to-text) - diarized_json format
