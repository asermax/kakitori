# Design: PROCESS-002 - Multi-LLM Provider Support

**Feature Spec**: [../feature-specs/PROCESS-002.md](../feature-specs/PROCESS-002.md)
**Status**: Approved

---

## Purpose

This document captures the design rationale for adding multi-provider support to kakitori's transcription system, allowing users to choose between Gemini and OpenAI for audio transcription with speaker diarization.

## Problem Context

The current implementation is tightly coupled to the Google Gemini API via the `google-genai` SDK. Users face several challenges:

1. **Provider lock-in**: No ability to choose alternative providers based on cost, performance, or availability
2. **API availability**: Different providers may have different regional availability or quota limits
3. **Feature parity**: Different providers excel at different tasks (e.g., speed vs accuracy trade-offs)
4. **Migration risk**: Direct SDK coupling makes it difficult to switch providers if needed

**Constraints:**

- OpenAI support should be optional (not all users need it)
- Both providers must produce identical output format (transparent to downstream code)
- Provider selection should be simple (environment variable configuration)
- Must preserve multi-turn transcription capability for long recordings
- No backward compatibility fallbacks - clean configuration with new environment variables

**Interactions:**

- Replaces direct `google-genai` SDK usage with unified provider abstraction
- Maintains compatibility with existing speaker identification workflow (PROCESS-001)
- Uses optional dependencies to avoid forcing OpenAI installation on all users

## Design Overview

The solution introduces a provider abstraction layer that isolates provider-specific logic while presenting a unified interface to the rest of the application.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Process Command Package                      │
│                                                                  │
│  Audio File + Config                                            │
│      │                                                           │
│      ▼                                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PROVIDER FACTORY                                         │   │
│  │   get_provider(provider_name, api_key)                   │   │
│  │                                                           │   │
│  │   ┌─────────────┐   ┌─────────────┐                      │   │
│  │   │   Gemini    │   │   OpenAI    │                      │   │
│  │   │  Provider   │   │  Provider   │                      │   │
│  │   │             │   │ (optional)  │                      │   │
│  │   │ llm library │   │  openai SDK │                      │   │
│  │   └─────────────┘   └─────────────┘                      │   │
│  └────────────┬────────────────────────────────────────────┘   │
│               │ TranscriptionProvider interface                 │
│               │   .transcribe(audio_path, participant_count)    │
│               │   .requires_cleanup() → bool                    │
│               │   .cleanup() → None                             │
│               ▼                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ TRANSCRIPTION                                            │   │
│  │   Unified Transcription model (Pydantic)                 │   │
│  │   - segments: list[TranscriptSegment]                    │   │
│  └──────┬──────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  [Speaker Identification → Format → Output]                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Architecture layers:**

| Layer | Responsibility | Location |
|-------|----------------|----------|
| **Factory** | Provider instantiation, import validation | `providers/__init__.py` |
| **Base Interface** | Abstract provider contract | `providers/__init__.py` |
| **Gemini Provider** | llm library integration, multi-turn logic | `providers/gemini.py` |
| **OpenAI Provider** | openai SDK integration, response parsing | `providers/openai.py` |
| **Process Command** | Pipeline orchestration (unchanged) | `process/command.py` |

## Data Flow

### Input Validation (Before Provider Call)

```
Audio Path + participant_count
    │
    ▼
┌────────────────────────────────────────────────────┐
│ File Existence Check                                │
│   if not Path(audio_path).exists():                │
│       raise "Audio file not found: {path}"         │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ File Readability Check                              │
│   try: open(audio_path, "rb")                      │
│   except PermissionError:                          │
│       raise "Cannot read audio file: {path}"       │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ File Size Check                                     │
│   if Path(audio_path).stat().st_size == 0:         │
│       raise "Audio file is empty or has 0 duration"│
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Audio Format Check                                  │
│   suffix = Path(audio_path).suffix.lower()         │
│   if suffix not in SUPPORTED_FORMATS:              │
│       raise "Unsupported audio format for {provider}"│
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Participant Count Check                             │
│   if participant_count <= 0:                       │
│       raise "Participant count must be positive"   │
└────────────────────────────────────────────────────┘
    │
    ▼
Provider.transcribe(audio_path, participant_count)
```

**Validation implementation**:

```python
def validate_audio_input(
    audio_path: str,
    participant_count: int,
    provider_name: str
) -> None:
    """Validate audio file and parameters before transcription.

    Raises:
        FileNotFoundError: Audio file does not exist
        PermissionError: Audio file not readable
        ValueError: Empty file, invalid format, or invalid participant_count
    """
    path = Path(audio_path)

    # File existence
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # File readability
    try:
        with open(path, "rb") as f:
            f.read(1)  # Try to read 1 byte
    except PermissionError:
        raise PermissionError(
            f"Cannot read audio file: {audio_path}. Check permissions."
        )

    # Empty file check
    if path.stat().st_size == 0:
        raise ValueError("Audio file is empty or has 0 duration.")

    # Format check (provider-specific)
    supported = SUPPORTED_FORMATS.get(provider_name, set())
    if path.suffix.lower() not in supported:
        formats = ", ".join(sorted(supported))
        raise ValueError(
            f"Unsupported audio format for {provider_name}. "
            f"Supported: {formats}"
        )

    # Participant count
    if participant_count <= 0:
        raise ValueError(
            f"Participant count must be positive (got {participant_count})"
        )
```

**Location**: `src/kakitori/providers/validation.py`

**Supported formats per provider**:

```python
SUPPORTED_FORMATS = {
    "gemini": {".mp3", ".wav", ".m4a", ".ogg", ".flac"},
    "openai": {".flac", ".mp3", ".mp4", ".mpeg", ".mpga",
               ".m4a", ".ogg", ".wav", ".webm"},
}
```

### Provider Selection and Instantiation

```
Environment Variables
    │
    ├─ KAKITORI_PROVIDER (default: "gemini")
    └─ KAKITORI_PROVIDER_KEY (required)
    │
    ▼
┌────────────────────────────────────────────────────┐
│ get_provider(provider_name, api_key)                │
│                                                     │
│   if provider_name == "gemini":                    │
│       return GeminiProvider(api_key)               │
│                                                     │
│   elif provider_name == "openai":                  │
│       try:                                         │
│           from .openai import OpenAIProvider       │
│       except ImportError:                          │
│           raise "Install with: pip install [openai]"│
│       return OpenAIProvider(api_key)               │
│                                                     │
│   else:                                            │
│       raise "Unsupported provider"                 │
└────────────────────────────────────────────────────┘
    │
    ▼
TranscriptionProvider instance
```

### Gemini Provider Flow (via llm library)

```
Audio File
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Configure llm Library                               │
│   os.environ["GEMINI_API_KEY"] = self.api_key      │
│   model = llm.get_model("gemini-3-flash-preview")  │
│   conversation = model.conversation()              │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ First Turn: Audio + Prompt + Schema                 │
│   attachment = llm.Attachment.from_file(audio_path)│
│   response = conversation.prompt(                  │
│       prompt=initial_prompt,                       │
│       attachments=[attachment],                    │
│       schema=Transcription,                        │
│       temperature=0.3,         # Prevent loops     │
│       max_output_tokens=65536  # ~2hr meetings     │
│   )                                                │
│   data = json.loads(response.text())               │
│   transcription = Transcription.model_validate(data)│
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Multi-Turn Loop (max 100 turns)                     │
│   while transcription.segments:                    │
│       response = conversation.prompt(              │
│           CONTINUATION_PROMPT,                     │
│           schema=Transcription,                    │
│           temperature=0.3,                         │
│           max_output_tokens=65536                  │
│       )                                            │
│       more_data = json.loads(response.text())      │
│       more_segments = Transcription.model_validate()│
│       if not more_segments.segments: break         │
│       all_segments.extend(more_segments.segments)  │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Cleanup Environment                                 │
│   os.environ["GEMINI_API_KEY"] = original_value    │
└────────────────────────────────────────────────────┘
    │
    ▼
Transcription(segments=all_segments)
```

**Key aspects:**
- llm library handles file upload to Gemini Files API automatically
- Files have 48-hour TTL, auto-expire (no manual cleanup needed)
- Schema parameter accepts Pydantic models directly
- Response parsing: `json.loads(response.text())` then validate
- `temperature=0.3` prevents repetition loops in multi-turn (ADR-004)
- `max_output_tokens=65536` supports long meetings (~2 hours)
- Environment variable restoration ensures no side effects

### OpenAI Provider Flow (via openai SDK)

```
Audio File
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Initialize Client                                   │
│   client = OpenAI(api_key=self.api_key)            │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Single Request with Auto Chunking                   │
│   with open(audio_path, "rb") as audio_file:       │
│       response = client.audio.transcriptions.create(│
│           model="gpt-4o-transcribe-diarize",       │
│           file=audio_file,                         │
│           response_format="diarized_json",         │
│           chunking_strategy="auto"                 │
│       )                                            │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Parse diarized_json Response                        │
│   Validate: response.segments exists               │
│   Build speaker mapping (order of first appearance)│
│     A → Speaker 1                                  │
│     B → Speaker 2                                  │
│     E → Speaker 3  (handles gaps)                  │
│   Calculate total duration for timestamp format    │
│     >= 60 min → HH:MM:SS                           │
│     <  60 min → MM:SS                              │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ Convert to Unified Format                           │
│   segments = []                                     │
│   for seg in response.segments:                    │
│       segments.append(TranscriptSegment(           │
│           start_time=format_timestamp(seg.start),  │
│           speaker=speaker_map[seg.speaker],        │
│           content=seg.text                         │
│       ))                                           │
└────────────────────────────────────────────────────┘
    │
    ▼
Transcription(segments=segments)
```

**Key aspects:**
- Single API call (chunking handled internally by OpenAI)
- Speaker labels (A, B, C...) mapped to "Speaker 1", "Speaker 2", etc.
- Non-consecutive labels handled transparently (A, B, E → Speaker 1, 2, 3)
- Timestamps converted from seconds to MM:SS or HH:MM:SS format
- No cleanup needed (OpenAI handles file management internally)

### Prompt Templates

**Gemini Initial Prompt** (used on first turn with audio attachment):

```python
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
```

**Gemini Continuation Prompt** (used on subsequent turns):

```python
CONTINUATION_PROMPT = """
Continue transcribing from where you left off.
If there is no more audio to transcribe, return an empty segments array.
""".strip()
```

**OpenAI**: No prompt needed - diarization is built into the `gpt-4o-transcribe-diarize` model. Uses API parameters (`chunking_strategy`, `response_format`) instead of prompting.

## Modeling

### Provider Abstraction

```python
from abc import ABC, abstractmethod
from kakitori.models import Transcription

class TranscriptionProvider(ABC):
    """Abstract base for transcription providers."""

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        participant_count: int
    ) -> Transcription:
        """Transcribe audio file with speaker diarization.

        Providers handle cleanup internally if needed.
        Returns unified Transcription model.
        """
        pass

    def requires_cleanup(self) -> bool:
        """Whether provider needs cleanup after transcription.

        Override if provider uploads files requiring manual deletion.
        Default: False (no cleanup needed)
        """
        return False

    def cleanup(self) -> None:
        """Cleanup uploaded files/resources.

        Only called if requires_cleanup() returns True.
        Override for providers that upload files needing deletion.
        """
        pass
```

**Design rationale:**
- `transcribe()` is the core interface - must be implemented
- `requires_cleanup()` defaults to False (graceful degradation)
- `cleanup()` is optional - only needed for providers with manual file management
- Return type is always `Transcription` (unified model)

### Configuration

**Configuration sources (priority order):**
1. System environment variables (highest)
2. Local `.env` file
3. Global `~/.config/kakitori/.env`

**Environment variables:**
- `KAKITORI_PROVIDER` → provider_name (default: "gemini")
- `KAKITORI_PROVIDER_KEY` → api_key (required, no default)

**Configuration loading** (in `process/command.py`):

```python
def run_process(audio_path: str, participant_count: int, ...) -> None:
    # Load provider configuration from environment
    provider_name = os.getenv("KAKITORI_PROVIDER", "gemini")
    api_key = os.getenv("KAKITORI_PROVIDER_KEY")

    if not api_key:
        logger.error(
            "API key required. Set KAKITORI_PROVIDER_KEY environment variable."
        )
        sys.exit(1)

    # Validate inputs before provider instantiation
    validate_audio_input(audio_path, participant_count, provider_name)

    # Get provider and transcribe
    provider = get_provider(provider_name, api_key)
    transcription = provider.transcribe(audio_path, participant_count)
    # ... rest of pipeline ...
```

### Response Normalization

Both providers return the same unified format:

```python
class TranscriptSegment(BaseModel):
    start_time: str   # "MM:SS" or "HH:MM:SS"
    speaker: str      # "Speaker 1", "Speaker 2", or detected name
    content: str      # Transcribed text

class Transcription(BaseModel):
    segments: list[TranscriptSegment]
```

**Gemini**: Returns this format directly via structured output schema
**OpenAI**: Provider converts diarized_json → TranscriptSegment list

### Error Handling

Provider implementations wrap SDK-specific errors with user-friendly messages:

```python
class ProviderError(Exception):
    """Base exception for provider errors."""
    pass

class AuthenticationError(ProviderError):
    """Invalid API key."""
    pass

class RateLimitError(ProviderError):
    """Provider rate limit exceeded."""
    pass

class TranscriptionError(ProviderError):
    """Error during transcription."""
    pass
```

**Gemini error handling**:

```python
def transcribe(self, audio_path: str, participant_count: int) -> Transcription:
    try:
        # Get model - may fail if llm-gemini not installed
        try:
            model = llm.get_model("gemini-3-flash-preview")
        except llm.UnknownModelError as e:
            raise TranscriptionError(
                "Gemini model not available. "
                "Install llm-gemini: uv pip install llm-gemini>=0.28"
            ) from e

        # ... conversation setup and prompting ...
        response = conversation.prompt(...)
        data = json.loads(response.text())

        if not data:
            raise TranscriptionError(
                f"Failed to parse transcription response.\n"
                f"Response text: {response.text()[:500]}"
            )

        return Transcription.model_validate(data)

    except llm.ModelError as e:
        if "401" in str(e) or "authentication" in str(e).lower():
            raise AuthenticationError(
                "Invalid API key for Gemini. Check your KAKITORI_PROVIDER_KEY."
            ) from e
        elif "429" in str(e) or "rate" in str(e).lower():
            raise RateLimitError(
                "Gemini rate limit exceeded. Try again later."
            ) from e
        else:
            raise TranscriptionError(f"Gemini API error: {e}") from e

    except json.JSONDecodeError as e:
        raise TranscriptionError(
            f"Failed to parse Gemini response as JSON: {e}"
        ) from e

    except ValidationError as e:
        raise TranscriptionError(
            f"Gemini response doesn't match schema: {e}"
        ) from e
```

**OpenAI error handling**:

```python
def transcribe(self, audio_path: str, participant_count: int) -> Transcription:
    try:
        response = self.client.audio.transcriptions.create(...)

        if not hasattr(response, "segments") or not response.segments:
            raise TranscriptionError(
                "OpenAI response missing 'segments' array"
            )

        # ... parse response ...
        return Transcription(segments=segments)

    except openai.AuthenticationError as e:
        raise AuthenticationError(
            "Invalid API key for OpenAI. Check your KAKITORI_PROVIDER_KEY."
        ) from e

    except openai.RateLimitError as e:
        raise RateLimitError(
            "OpenAI rate limit exceeded. Try again later."
        ) from e

    except openai.APITimeoutError as e:
        raise TranscriptionError(
            "Network timeout while transcribing with OpenAI."
        ) from e

    except openai.BadRequestError as e:
        if "format" in str(e).lower():
            raise TranscriptionError(
                f"Unsupported audio format for OpenAI. "
                f"Supported: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm"
            ) from e
        raise TranscriptionError(f"OpenAI API error: {e}") from e
```

**Command-level error handling**:

```python
def run_process(audio_path: str, ...) -> None:
    try:
        validate_audio_input(audio_path, participant_count, provider_name)
        provider = get_provider(provider_name, api_key)
        transcription = provider.transcribe(audio_path, participant_count)
        # ... rest of pipeline ...

    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    except PermissionError as e:
        logger.error(str(e))
        sys.exit(1)

    except ValueError as e:  # Invalid format, empty file, bad participant_count
        logger.error(str(e))
        sys.exit(1)

    except AuthenticationError as e:
        logger.error(str(e))
        sys.exit(1)

    except RateLimitError as e:
        logger.error(str(e))
        sys.exit(1)

    except TranscriptionError as e:
        logger.error(str(e))
        sys.exit(1)
```

## Key Decisions

### Decision 1: llm Library for Gemini Instead of google-genai

**Choice**: Replace `google-genai` SDK with `llm` library + `llm-gemini` plugin.

**Alternatives considered:**
1. **Keep google-genai, add openai** - Two different SDK patterns (inconsistent)
2. **Write custom Gemini HTTP client** - Excessive maintenance burden
3. **Use llm library for both providers** - llm doesn't support OpenAI audio transcription API

**Why llm library**:
- Unified pattern for Gemini (llm) and OpenAI (native SDK)
- llm library provides clean schema support with Pydantic models
- llm-gemini handles file upload/cleanup automatically (48hr TTL)
- Multi-turn conversation API simplifies long recording handling
- Modern, actively maintained (v0.17+ with schema support from Feb 2025)

**Consequences**:
- **Migration required**: Replace google-genai dependency
- **API key configuration changes**: llm-gemini reads `GEMINI_API_KEY` from environment
- **File cleanup simplified**: No manual deletion needed (auto-expiry)
- **Model update**: Switch from `gemini-flash-latest` to `gemini-3-flash-preview` (Gemini 3 Flash is current generation)

**Related**: This enables consistent provider abstraction pattern

---

### Decision 2: OpenAI as Optional Dependency (Extras)

**Choice**: Make `openai` SDK an optional dependency installable via extras.

**Alternatives considered:**
1. **Make openai required for all users** - Forces dependency on users who only use Gemini
2. **Separate package for OpenAI support** - Fragmentation, maintenance overhead
3. **Runtime pip install** - Surprising behavior, poor user experience

**Why optional extras**:
- Users choose provider based on needs (not forced to install unused dependencies)
- Standard Python packaging pattern (widely understood)
- Clear installation: `uv tool install 'kakitori[openai]'`
- Graceful error messaging when missing

**Implementation**:
```toml
[project.optional-dependencies]
openai = ["openai>=1.60.0"]
```

**Error handling**:
```python
try:
    from .openai import OpenAIProvider
except ImportError:
    raise ImportError(
        "OpenAI provider requires optional dependencies.\n"
        "Install with: uv tool install 'kakitori[openai]'"
    )
```

**Consequences**:
- Smaller install size for Gemini-only users
- Clear upgrade path when switching providers
- Follows established patterns (FastAPI, SQLAlchemy)

**Related**: Aligns with Python packaging best practices

---

### Decision 3: Factory Pattern for Provider Instantiation

**Choice**: Use factory function `get_provider()` instead of direct instantiation.

**Alternatives considered:**
1. **Registry pattern with decorators** - Over-engineered for 2 providers
2. **Plugin system with entry points** - Unnecessary complexity, no third-party providers planned
3. **Direct instantiation in command** - Couples command logic to provider implementation

**Why factory pattern**:
- Centralizes provider selection logic
- Handles import validation (optional dependencies)
- Provides clear error messages for unsupported providers
- Extensible: new providers add `elif` clause

**Implementation**:
```python
def get_provider(provider_name: str, api_key: str) -> TranscriptionProvider:
    if provider_name == "gemini":
        from .gemini import GeminiProvider
        return GeminiProvider(api_key)
    elif provider_name == "openai":
        try:
            from .openai import OpenAIProvider
        except ImportError:
            raise ImportError(
                "OpenAI provider requires optional dependencies.\n"
                "Install with: uv tool install 'kakitori[openai]'"
            )
        return OpenAIProvider(api_key)
    else:
        raise ValueError(
            f"Unsupported provider: {provider_name}\n"
            f"Supported providers: gemini, openai"
        )
```

**Consequences**:
- Single point of provider instantiation
- Import errors caught and wrapped with helpful messages
- Process command remains simple (no provider knowledge)

**Related**: Standard creational pattern from Gang of Four

---

### Decision 4: Environment Variable for API Keys Per Provider

**Choice**: Use single `KAKITORI_PROVIDER_KEY` for selected provider.

**Alternatives considered:**
1. **Separate keys per provider** (GEMINI_API_KEY, OPENAI_API_KEY) - User must configure all, even unused
2. **Config file with nested keys** - More complex, requires file management
3. **Interactive prompt for missing keys** - Poor for automation/CI

**Why single key variable**:
- User only configures what they use
- Clear: "this is the key for my selected provider"
- Clean break: No legacy fallbacks to maintain
- Simple error: "Set KAKITORI_PROVIDER_KEY for your provider"

**Implementation note**:
Gemini provider sets `os.environ["GEMINI_API_KEY"]` internally (llm-gemini reads this), then restores original value after transcription to avoid side effects. This is an internal implementation detail - users configure `KAKITORI_PROVIDER_KEY` only.

**Consequences**:
- Cannot pre-configure multiple providers simultaneously
- Switching providers requires updating both KAKITORI_PROVIDER and KAKITORI_PROVIDER_KEY
- Simpler mental model for users

**Trade-off accepted**: Simplicity over multi-provider pre-configuration

---

### Decision 5: Cleanup Method Optional in Base Interface

**Choice**: Default `requires_cleanup()` to False, make `cleanup()` optional.

**Alternatives considered:**
1. **Always require cleanup implementation** - Forces boilerplate for providers without cleanup
2. **Remove cleanup from interface** - Cannot support providers needing cleanup
3. **Cleanup context manager** - Over-engineered, no concurrent provider usage

**Why optional cleanup**:
- Current providers (Gemini, OpenAI) don't need manual cleanup
- Gemini: llm-gemini files auto-expire (48hr TTL)
- OpenAI: Files handled internally by API
- Future providers might need cleanup - interface supports it
- Graceful degradation: providers implement only if needed

**Implementation**:
```python
# Default implementation (no cleanup)
def requires_cleanup(self) -> bool:
    return False

def cleanup(self) -> None:
    pass

# Command usage
provider = get_provider(provider_name, api_key)
transcription = provider.transcribe(audio_path, participant_count)

if provider.requires_cleanup():
    provider.cleanup()
```

**Consequences**:
- Minimal boilerplate for new providers
- Clear contract: "override if you need cleanup"
- Command code handles cleanup uniformly

**Related**: Template method pattern (optional hooks)

---

### Decision 6: Timestamp Format Normalization (MM:SS vs HH:MM:SS)

**Choice**: Convert OpenAI timestamps (seconds) to match Gemini format based on recording duration.

**Alternatives considered:**
1. **Always use HH:MM:SS** - Wastes space for short recordings ("00:03:45")
2. **Always use MM:SS** - Breaks for recordings over 60 minutes ("87:23" ambiguous)
3. **Preserve seconds format** - Inconsistent with existing Gemini output
4. **Let downstream code handle** - Pushes complexity to multiple consumers

**Why duration-based format**:
- Matches existing Gemini behavior (implicit format logic)
- Minimal visual clutter for short recordings
- Unambiguous for long recordings
- Consistent user experience across providers

**Implementation**:
```python
def _format_timestamp(self, seconds: float, use_hours: bool) -> str:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if use_hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        total_minutes = total_seconds // 60
        return f"{total_minutes:02d}:{secs:02d}"

# Usage
total_duration = max(seg.end for seg in response.segments)
use_hours = total_duration >= 3600  # 60 minutes
```

**Consequences**:
- OpenAI provider has timestamp conversion logic
- Format matches existing transcripts (no downstream changes)
- Edge case: 59:59 (MM:SS) → 01:00:00 (HH:MM:SS) at boundary

**Trade-off accepted**: Provider-specific logic for format consistency

---

### Decision 7: Speaker Label Mapping (Order of Appearance)

**Choice**: Map OpenAI labels (A, B, C...) to "Speaker 1", "Speaker 2"... based on first appearance order.

**Alternatives considered:**
1. **Alphabetical mapping** (A→1, B→2, C→3) - Breaks with non-consecutive labels (A, C, E)
2. **Preserve original labels** (A, B, C) - Inconsistent with Gemini output format
3. **Map by segment count** (most frequent → Speaker 1) - Changes order unpredictably
4. **Use timestamp order** (earliest → Speaker 1) - Same as appearance order for valid transcripts

**Why first appearance order**:
- Intuitive: "Speaker 1" is whoever speaks first
- Handles gaps: A, C, E → Speaker 1, 2, 3 (transparent)
- Matches Gemini behavior (speaker order matches conversation flow)
- Simple algorithm: dictionary insertion order (Python 3.11+)

**Implementation**:
```python
speaker_map = {}  # Preserves insertion order
for seg in response.segments:
    if seg.speaker not in speaker_map:
        speaker_number = len(speaker_map) + 1
        speaker_map[seg.speaker] = f"Speaker {speaker_number}"

    mapped_speaker = speaker_map[seg.speaker]
```

**Consequences**:
- Non-consecutive labels handled automatically
- Speaker 1 is always first speaker to talk
- Consistent with Gemini output expectations

**Edge case handling**: If OpenAI returns labels out of alphabetical order (B, A, C), mapping follows appearance: B→Speaker 1, A→Speaker 2, C→Speaker 3

---

## System Behavior

### Scenario: Gemini Provider (Default)

```
Given: User has KAKITORI_PROVIDER_KEY set
When: User runs `kakitori process meeting.mp3` (no provider specified)
Then:
  1. Defaults to Gemini provider
  2. llm library used with gemini-3-flash-preview model
  3. Multi-turn transcription for long recordings
  4. Files auto-expire after 48 hours (no manual cleanup)
  5. Output: Transcription with speaker labels
```

### Scenario: OpenAI Provider (Explicitly Selected)

```
Given: User has installed kakitori[openai]
  And: KAKITORI_PROVIDER=openai
  And: KAKITORI_PROVIDER_KEY=<openai-key>
When: User runs `kakitori process meeting.mp3`
Then:
  1. OpenAI provider instantiated
  2. Single API call with chunking_strategy=auto
  3. Response parsed to unified format
  4. Speaker labels mapped (A→Speaker 1, B→Speaker 2)
  5. Timestamps converted to MM:SS or HH:MM:SS
  6. Output: Transcription (identical format to Gemini)
```

### Scenario: OpenAI Not Installed

```
Given: User has not installed kakitori[openai]
  And: KAKITORI_PROVIDER=openai
When: User runs `kakitori process meeting.mp3`
Then:
  1. Factory function attempts import
  2. ImportError caught
  3. Error message displayed:
     "OpenAI provider requires optional dependencies.
      Install with: uv tool install 'kakitori[openai]'"
  4. Program exits with error code 1
```

### Scenario: Invalid Provider Name

```
Given: KAKITORI_PROVIDER=azure
When: User runs `kakitori process meeting.mp3`
Then:
  1. Factory function checks provider_name
  2. No match found
  3. Error message displayed:
     "Unsupported provider: azure
      Supported providers: gemini, openai"
  4. Program exits with error code 1
```

### Scenario: Missing API Key

```
Given: KAKITORI_PROVIDER=openai
  And: KAKITORI_PROVIDER_KEY is not set
When: User runs `kakitori process meeting.mp3`
Then:
  1. Configuration loading detects missing key
  2. Error message displayed:
     "API key required. Set KAKITORI_PROVIDER_KEY environment variable."
  3. Program exits with error code 1
```

### Scenario: Provider API Error (Rate Limit)

```
Given: Valid OpenAI configuration
When: User exceeds API rate limit
Then:
  1. openai.RateLimitError raised by SDK
  2. Provider catches and wraps error
  3. Error message displayed:
     "OpenAI rate limit exceeded. Try again later."
  4. Program exits with error code 1
```

### Scenario: Speaker Count Mismatch

```
Given: OpenAI provider detects 3 speakers
  And: participant_count=2 (user expected 2 speakers)
When: Transcription completes
Then:
  1. Provider detects mismatch
  2. Warning logged:
     "Detected 3 speakers but expected 2"
  3. Transcription proceeds with 3 speakers
  4. User sees warning in logs (if -v flag)
```

### Scenario: OpenAI with 5+ Speakers

```
Given: Recording has 5 or more speakers
  And: User selects OpenAI provider
When: Transcription is performed
Then:
  1. OpenAI gpt-4o-transcribe-diarize processes the audio
  2. Model returns up to 4 distinct speaker labels (A, B, C, D)
  3. Additional speakers may be grouped with existing labels
  4. Warning logged:
     "OpenAI detected 4 speakers (max supported).
      Recordings with >4 speakers may have reduced diarization accuracy."
  5. Transcription proceeds with available speaker labels
  6. User sees warning suggesting Gemini for multi-speaker recordings
```

**Note**: OpenAI's `gpt-4o-transcribe-diarize` officially supports up to 4 speakers. For recordings with more speakers, recommend Gemini which has no documented speaker limit.

## Pattern Alignment

### Existing Patterns Used

**DES-001: Lazy Command Imports**
- Applied: Provider modules imported inside factory function
- Benefit: Optional dependencies not loaded unless provider selected
- Example: `from .openai import OpenAIProvider` inside `elif` block

**ADR-004: Multi-Turn Chat for Long Recordings**
- Preserved: Gemini provider maintains multi-turn conversation approach
- Implementation: Uses `llm.model.conversation()` API
- Continuation: Same prompt strategy ("Continue transcribing...")

**ADR-002: Multi-Source Configuration Merge**
- Extended: KAKITORI_PROVIDER and KAKITORI_PROVIDER_KEY follow existing config priority
- Order: System env > local .env > global config
- Replaces: GEMINI_API_KEY (no longer used)

### New Patterns Emerging

**Provider Abstraction with Optional Implementations**
- Pattern: ABC base class + factory + optional extras
- Applicability: Future multi-backend features (e.g., storage providers, audio backends)
- Considerations: Could become DES-007 if pattern proves reusable

**Response Normalization in Adapters**
- Pattern: Provider-specific parsing → unified internal model
- Benefit: Downstream code (speaker ID, formatting) unaware of provider
- Trade-off: Conversion logic lives in provider implementations

**Graceful Optional Dependency Errors**
- Pattern: Try-import with helpful error messages including installation instructions
- Follows: pandas, FastAPI, SQLAlchemy patterns
- User experience: Clear path to resolution

## Migration Notes

### Breaking Changes

1. **Dependency change**: `google-genai` removed, replaced by `llm` + `llm-gemini`
2. **API key environment variable**: `GEMINI_API_KEY` replaced by `KAKITORI_PROVIDER_KEY` (no fallback)
3. **Return signature change**: `transcribe_audio()` returns `Transcription` instead of `(Transcription, file_name)` tuple
4. **Model change**: `gemini-flash-latest` → `gemini-3-flash-preview`

### Migration Path for Users

**Continue with Gemini:**
```bash
# Update environment variables
KAKITORI_PROVIDER=gemini  # Optional, this is default
KAKITORI_PROVIDER_KEY=your-gemini-key

# Remove old variable
# GEMINI_API_KEY is no longer used
```

**Switch to OpenAI:**
```bash
# Install extras
uv tool install 'kakitori[openai]'

# Configure
KAKITORI_PROVIDER=openai
KAKITORI_PROVIDER_KEY=your-openai-key
```

### Code Migration (Internal)

**Before:**
```python
from kakitori.process.transcribe import transcribe_audio, cleanup_file

transcription, file_name = transcribe_audio(audio_path, api_key, participant_count)
# ... speaker identification ...
cleanup_file(api_key, file_name)
```

**After:**
```python
from kakitori.providers import get_provider

provider = get_provider(provider_name, api_key)
transcription = provider.transcribe(audio_path, participant_count)
# ... speaker identification ...

if provider.requires_cleanup():
    provider.cleanup()
```

### Dependency Updates

**Remove:**
- `google-genai`

**Add (required):**
- `llm>=0.17` (schema support, Feb 2025+)
- `llm-gemini>=0.28` (Gemini 3 Flash support)

**Add (optional):**
- `openai>=1.60.0` (gpt-4o-transcribe-diarize model)

**Unchanged:**
- `pydantic>=2.0` (already required)

## Notes

### Uncertainties

- **llm-gemini file cleanup behavior**: Documentation states 48hr TTL, but no explicit confirmation of auto-deletion (observed behavior suggests it works, needs verification)
- **llm library version compatibility**: Schema support added in 0.17 (Feb 2025) - should we pin more strictly?
- **Gemini 3 Flash availability timeline**: Currently in preview - when does it become stable? Should we fall back to 2.0 Flash?

### Assumptions

- Users understand optional dependencies concept (extras)
- Environment variable configuration is acceptable UX
- Both providers produce compatible diarization quality
- Python 3.11+ (dict insertion order guarantee for speaker mapping)

### Areas Needing Clarification

- **Provider-specific prompting**: Should we expose provider-specific parameters (e.g., OpenAI's known_speaker_references)?
- **Cost tracking**: Should we log provider used + duration for cost estimation?
- **Provider validation testing**: How to test providers without requiring API keys in CI?
- **Error standardization**: Should we create ProviderError hierarchy (similar to SQLAlchemy dialect errors)?
- **Future providers**: If adding AssemblyAI, Deepgram, etc., should cleanup interface change? (they may need webhooks/polling)

### Research Sources

- llm library schema support: [Simon Willison's article](https://simonwillison.net/2025/Feb/28/llm-schemas/)
- llm-gemini plugin: [GitHub releases](https://github.com/simonw/llm-gemini/releases)
- OpenAI diarization: [GPT-4o Transcribe Diarize docs](https://platform.openai.com/docs/models/gpt-4o-transcribe-diarize)
- Python optional dependencies: PEP 631, FastAPI/SQLAlchemy patterns
- Provider abstraction: SQLAlchemy dialect system, Requests adapters
