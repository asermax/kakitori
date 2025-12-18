from dataclasses import dataclass

import questionary
from questionary import Choice, Separator
from rich.console import Console
from rich.table import Table

from .audio import parse_timestamp, play_snippet
from kakitori.logging import logger
from kakitori.models import Transcription, TranscriptSegment

# Pagination constant
SEGMENTS_PER_PAGE = 10


@dataclass
class SpeakerState:
    """Tracks identification state for a single speaker."""

    label: str
    assigned_name: str | None
    segment_indices: list[int]


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


def _build_speaker_states(
    transcription: Transcription,
) -> list[SpeakerState]:
    """Extract unique speakers and their segment indices from transcription.

    Args:
        transcription: Transcription with all segments

    Returns:
        List of SpeakerState objects, sorted by label
    """
    speaker_indices: dict[str, list[int]] = {}

    for idx, segment in enumerate(transcription.segments):
        if segment.speaker not in speaker_indices:
            speaker_indices[segment.speaker] = []
        speaker_indices[segment.speaker].append(idx)

    # Sort by speaker label and keep all segment indices
    return [
        SpeakerState(
            label=speaker,
            assigned_name=None,
            segment_indices=indices,
        )
        for speaker, indices in sorted(speaker_indices.items())
    ]


def _display_speakers_table(speaker_states: list[SpeakerState]) -> None:
    """Display rich table showing speaker status.

    Args:
        speaker_states: List of speaker states to display
    """
    console = Console()
    table = Table(title="Speaker Identification", show_header=True)

    table.add_column("Speaker", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Segments", justify="right")

    for state in speaker_states:
        if state.assigned_name is not None:
            status = f"[green]:heavy_check_mark: {state.assigned_name}[/green]"
        else:
            status = "[yellow]???[/yellow]"

        table.add_row(
            state.label,
            status,
            str(len(state.segment_indices)),
        )

    console.print(table)
    console.print()


def _display_segments_table(
    speaker_state: SpeakerState,
    transcription: Transcription,
    page: int,
) -> tuple[list[int], int]:
    """Display paginated segments table.

    Args:
        speaker_state: Speaker state with segment indices
        transcription: Full transcription
        page: Current page number (0-indexed)

    Returns:
        Tuple of (segment_indices_on_page, total_pages)
    """
    console = Console()
    all_indices = speaker_state.segment_indices
    total = len(all_indices)
    total_pages = (total + SEGMENTS_PER_PAGE - 1) // SEGMENTS_PER_PAGE

    start = page * SEGMENTS_PER_PAGE
    end = min(start + SEGMENTS_PER_PAGE, total)
    page_indices = all_indices[start:end]

    status = speaker_state.assigned_name or "Not assigned"
    console.print(f"\n[bold]{speaker_state.label}[/bold] - {status}")
    console.print(f"Page {page + 1} of {total_pages} ({total} total segments)\n")

    table = Table(show_header=True)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Time", style="yellow")
    table.add_column("Content")

    for i, idx in enumerate(page_indices, 1):
        segment = transcription.segments[idx]
        content = segment.content[:60] + "..." if len(segment.content) > 60 else segment.content
        table.add_row(str(i), segment.start_time, f'"{content}"')

    console.print(table)
    console.print()

    return page_indices, total_pages


def _play_segment(
    segment_idx: int,
    transcription: Transcription,
    audio_path: str,
) -> None:
    """Play a single segment audio snippet.

    Args:
        segment_idx: Index of the segment to play
        transcription: Full transcription
        audio_path: Path to audio file
    """
    segment = transcription.segments[segment_idx]
    start_seconds = parse_timestamp(segment.start_time)
    duration = get_snippet_duration(
        transcription.segments,
        segment_idx,
        max_duration=5.0,
    )

    logger.debug(f"Playing segment {segment_idx}: start={start_seconds:.2f}s, duration={duration:.2f}s")
    play_snippet(audio_path, start_seconds, duration=duration)


def _play_all_snippets(
    speaker_state: SpeakerState,
    transcription: Transcription,
    audio_path: str,
) -> None:
    """Play all snippets for a speaker sequentially.

    Args:
        speaker_state: Speaker whose snippets to play
        transcription: Full transcription
        audio_path: Path to audio file
    """
    console = Console()
    console.print(f"\n[bold]Playing {len(speaker_state.segment_indices)} snippet(s)...[/bold]\n")

    for i, segment_idx in enumerate(speaker_state.segment_indices, 1):
        segment = transcription.segments[segment_idx]
        console.print(f"Snippet {i}/{len(speaker_state.segment_indices)}: [{segment.start_time}]")

        _play_segment(segment_idx, transcription, audio_path)

    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def _play_page_snippets(
    page_indices: list[int],
    transcription: Transcription,
    audio_path: str,
) -> None:
    """Play all snippets on current page sequentially.

    Args:
        page_indices: Segment indices for current page
        transcription: Full transcription
        audio_path: Path to audio file
    """
    console = Console()
    console.print(f"\n[bold]Playing {len(page_indices)} snippet(s) from this page...[/bold]\n")

    for i, segment_idx in enumerate(page_indices, 1):
        segment = transcription.segments[segment_idx]
        console.print(f"Snippet {i}/{len(page_indices)}: [{segment.start_time}]")

        _play_segment(segment_idx, transcription, audio_path)

    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def _show_main_menu(speaker_states: list[SpeakerState]) -> str | None:
    """Display main menu and return selected value.

    Args:
        speaker_states: List of speaker states

    Returns:
        Selected value: speaker label, "confirm", "cancel", or None if quit
    """
    _display_speakers_table(speaker_states)

    choices = []

    for state in speaker_states:
        if state.assigned_name is not None:
            title = f"[x] {state.label} - {state.assigned_name}"
        else:
            title = f"[ ] {state.label} - ???"

        choices.append(Choice(title=title, value=state.label))

    choices.append(Separator())
    choices.append(Choice("Confirm and continue", value="confirm"))
    choices.append(Choice("Cancel", value="cancel"))

    return questionary.select(
        "Select a speaker to identify:",
        choices=choices,
    ).ask()


def _show_speaker_detail_menu(
    speaker_state: SpeakerState,
    transcription: Transcription,
    audio_path: str,
) -> str | None:
    """Display paginated speaker detail menu and handle interactions.

    Args:
        speaker_state: Speaker to work with
        transcription: Full transcription
        audio_path: Path to audio file

    Returns:
        Assigned name if user assigns one, None if user goes back
    """
    page = 0

    while True:
        page_indices, total_pages = _display_segments_table(
            speaker_state,
            transcription,
            page,
        )

        choices = [
            Choice("Play segment (enter number)", value="play"),
            Choice("Play all on this page", value="play_page"),
            Separator(),
        ]

        if page < total_pages - 1:
            choices.append(Choice("Next page →", value="next"))

        if page > 0:
            choices.append(Choice("← Previous page", value="prev"))

        choices.append(Separator())
        choices.append(Choice("Assign name", value="assign"))
        choices.append(Choice("Back to main menu", value="back"))

        result = questionary.select("Action:", choices=choices).ask()

        if result is None or result == "back":
            return None

        if result == "play":
            num = questionary.text(
                f"Enter segment number (1-{len(page_indices)}):",
            ).ask()

            if num and num.isdigit():
                idx = int(num) - 1

                if 0 <= idx < len(page_indices):
                    _play_segment(page_indices[idx], transcription, audio_path)

        elif result == "play_page":
            _play_page_snippets(page_indices, transcription, audio_path)

        elif result == "next":
            page += 1

        elif result == "prev":
            page -= 1

        elif result == "assign":
            name = questionary.text(f"Who is {speaker_state.label}?").ask()

            if name and name.strip():
                return name.strip()


def identify_speakers(
    transcription: Transcription,
    audio_path: str,
) -> dict[str, str]:
    """Interactive menu-driven speaker identification.

    Args:
        transcription: Transcription with generic speaker labels
        audio_path: Path to the audio file

    Returns:
        Dictionary mapping generic speaker labels to assigned names.
        Returns empty dict if cancelled.
    """
    speaker_states = _build_speaker_states(transcription)

    if not speaker_states:
        logger.info("No speakers found in transcription")
        return {}

    logger.info(f"Found {len(speaker_states)} speakers to identify")

    # Create a mapping from label to state for easy lookup
    state_by_label = {state.label: state for state in speaker_states}

    while True:
        selection = _show_main_menu(speaker_states)

        # User cancelled with Escape/Ctrl+C
        if selection is None:
            if questionary.confirm("Cancel identification? Generic labels will be kept.").ask():
                logger.info("Speaker identification cancelled")
                return {}
            else:
                continue

        # User selected "Confirm"
        if selection == "confirm":
            break

        # User selected "Cancel"
        if selection == "cancel":
            if questionary.confirm("Cancel identification? Generic labels will be kept.").ask():
                logger.info("Speaker identification cancelled")
                return {}
            else:
                continue

        # User selected a speaker
        speaker_state = state_by_label.get(selection)

        if speaker_state is not None:
            assigned_name = _show_speaker_detail_menu(
                speaker_state,
                transcription,
                audio_path,
            )

            if assigned_name is not None:
                speaker_state.assigned_name = assigned_name
                logger.info(f"{speaker_state.label} identified as: {assigned_name}")

    # Build and return mapping (only assigned speakers)
    return {
        state.label: state.assigned_name
        for state in speaker_states
        if state.assigned_name is not None
    }


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
