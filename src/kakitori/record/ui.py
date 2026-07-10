from pathlib import Path

import questionary
from questionary import Choice
from rich.console import Console
from rich.table import Table

from kakitori.record.sources import AudioSource, AvailableSources


def display_sources_table(
    sources: AvailableSources,
    selected_input: AudioSource,
    selected_monitor: AudioSource,
) -> None:
    """Display rich table showing available and selected sources.

    Args:
        sources: All available sources
        selected_input: Currently selected input source
        selected_monitor: Currently selected monitor source
    """
    console = Console()

    console.print("\n[bold]Selected Audio Sources:[/bold]\n")

    table = Table(show_header=True)
    table.add_column("Type", style="cyan")
    table.add_column("Source", style="yellow")
    table.add_column("State")

    input_marker = "[green]●[/green]" if selected_input.state == "RUNNING" else "○"
    monitor_marker = (
        "[green]●[/green]" if selected_monitor.state == "RUNNING" else "○"
    )

    table.add_row(
        "[I] Input (mic)",
        f"{input_marker} {selected_input.name}",
        selected_input.state,
    )

    table.add_row(
        "[M] Monitor (system)",
        f"{monitor_marker} {selected_monitor.name}",
        selected_monitor.state,
    )

    console.print(table)
    console.print()


def select_source(
    sources: list[AudioSource],
    source_type: str,
) -> AudioSource:
    """Let user select a source from a list using questionary.

    Args:
        sources: List of available sources
        source_type: "input" or "monitor" for display

    Returns:
        Selected AudioSource
    """
    choices = []

    for source in sources:
        state_marker = "[RUNNING]" if source.state == "RUNNING" else ""
        label = f"{source.name} {state_marker}".strip()
        choices.append(Choice(title=label, value=source))

    return questionary.select(
        f"Select {source_type} source:",
        choices=choices,
    ).unsafe_ask()


def confirm_sources(
    sources: AvailableSources,
    input_source: AudioSource,
    monitor_source: AudioSource,
) -> tuple[AudioSource, AudioSource]:
    """Interactive menu to confirm or change source selection.

    Args:
        sources: All available sources
        input_source: Initial input source
        monitor_source: Initial monitor source

    Returns:
        Tuple of (selected_input, selected_monitor)
    """
    while True:
        display_sources_table(sources, input_source, monitor_source)

        choices = [
            Choice("Continue with these sources", value="continue"),
            Choice("Change input source [I]", value="input"),
            Choice("Change monitor source [M]", value="monitor"),
        ]

        action = questionary.select(
            "Confirm audio sources:",
            choices=choices,
        ).unsafe_ask()

        if action == "continue":
            return input_source, monitor_source

        if action == "input":
            new_input = select_source(sources.inputs, "input")

            if new_input is not None:
                input_source = new_input

        elif action == "monitor":
            new_monitor = select_source(sources.monitors, "monitor")

            if new_monitor is not None:
                monitor_source = new_monitor


def prompt_save_location(default_name: str) -> Path:
    """Prompt user for output filename.

    Args:
        default_name: Default filename suggestion

    Returns:
        Full path for output file
    """
    save_dir = Path.cwd()

    console = Console()
    console.print(f"\n[bold]Save location:[/bold] {save_dir}")
    console.print(f"[dim]Default filename: {default_name}[/dim]\n")

    filename = questionary.text(
        "Enter filename (or press Enter for default):",
        default=default_name,
    ).unsafe_ask()

    if not filename.strip():
        filename = default_name

    filename = filename.strip()

    if not filename.endswith(".ogg"):
        filename = f"{filename}.ogg"

    return save_dir / filename
