import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class AudioSource:
    """Represents a PulseAudio/PipeWire audio source."""

    id: str
    name: str
    driver: str
    format: str
    state: str


@dataclass
class AvailableSources:
    """Container for input and monitor sources."""

    inputs: list[AudioSource]
    monitors: list[AudioSource]


def check_dependencies() -> list[str]:
    """Check for required system dependencies.

    Returns:
        List of missing dependency names (empty if all present)
    """
    missing = []

    if shutil.which("pactl") is None:
        missing.append("pactl")

    if shutil.which("ffmpeg") is None:
        missing.append("ffmpeg")

    return missing


def get_sources() -> AvailableSources:
    """Get available PulseAudio/PipeWire sources, separated by type.

    Returns:
        AvailableSources with inputs and monitors

    Raises:
        RuntimeError: If pactl command fails
    """
    result = subprocess.run(
        ["pactl", "list", "short", "sources"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"pactl command failed: {result.stderr}")

    inputs = []
    monitors = []

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue

        parts = line.split("\t")

        if len(parts) < 5:
            continue

        source = AudioSource(
            id=parts[0],
            name=parts[1],
            driver=parts[2],
            format=parts[3],
            state=parts[4],
        )

        if ".monitor" in source.name:
            monitors.append(source)
        else:
            inputs.append(source)

    return AvailableSources(inputs=inputs, monitors=monitors)


def find_running_source(sources: list[AudioSource]) -> AudioSource | None:
    """Find the first RUNNING source in a list.

    Args:
        sources: List of audio sources

    Returns:
        First source with RUNNING state, or first source if none running, or None if empty
    """
    for source in sources:
        if source.state == "RUNNING":
            return source

    return sources[0] if sources else None
