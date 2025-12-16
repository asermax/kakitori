import logging
import shutil
import subprocess
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class CombinedSink:
    """Module IDs for a combined PulseAudio sink."""

    sink_id: int
    input_loopback_id: int
    monitor_loopback_id: int
    monitor_source: str


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


def create_combined_sink(input_source: str, monitor_source: str) -> CombinedSink:
    """Create a null sink and loopbacks to combine two audio sources.

    This creates a temporary PulseAudio sink that mixes microphone input
    and system audio monitor into a single source for recording.

    Args:
        input_source: Name of the microphone source
        monitor_source: Name of the system audio monitor source

    Returns:
        CombinedSink with module IDs and monitor source name

    Raises:
        RuntimeError: If pactl commands fail
    """
    sink_name = "kakitori_combined"

    # Create null sink
    logger.info("Creating combined PulseAudio sink")
    result = subprocess.run(
        [
            "pactl",
            "load-module",
            "module-null-sink",
            f"sink_name={sink_name}",
            "sink_properties=device.description=Kakitori\\ Recording",
            "rate=48000",
            "channels=2",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to create null sink: {result.stderr}")

    sink_id = int(result.stdout.strip())
    logger.debug(f"Created null sink with ID {sink_id}")

    # Create loopback from input to null sink
    result = subprocess.run(
        [
            "pactl",
            "load-module",
            "module-loopback",
            f"source={input_source}",
            f"sink={sink_name}",
            "latency_msec=100",
            "adjust_time=5",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Cleanup sink before raising
        subprocess.run(["pactl", "unload-module", str(sink_id)])
        raise RuntimeError(f"Failed to create input loopback: {result.stderr}")

    input_loopback_id = int(result.stdout.strip())
    logger.debug(f"Created input loopback with ID {input_loopback_id}")

    # Create loopback from monitor to null sink
    result = subprocess.run(
        [
            "pactl",
            "load-module",
            "module-loopback",
            f"source={monitor_source}",
            f"sink={sink_name}",
            "latency_msec=100",
            "adjust_time=5",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Cleanup both sink and first loopback before raising
        subprocess.run(["pactl", "unload-module", str(input_loopback_id)])
        subprocess.run(["pactl", "unload-module", str(sink_id)])
        raise RuntimeError(f"Failed to create monitor loopback: {result.stderr}")

    monitor_loopback_id = int(result.stdout.strip())
    logger.debug(f"Created monitor loopback with ID {monitor_loopback_id}")

    monitor_name = f"{sink_name}.monitor"
    logger.info(f"Combined sink ready: {monitor_name}")

    return CombinedSink(
        sink_id=sink_id,
        input_loopback_id=input_loopback_id,
        monitor_loopback_id=monitor_loopback_id,
        monitor_source=monitor_name,
    )


def cleanup_combined_sink(combined: CombinedSink) -> None:
    """Unload the null sink and loopback modules.

    Args:
        combined: CombinedSink with module IDs to unload
    """
    logger.info("Cleaning up combined PulseAudio sink")

    # Unload in reverse order: loopbacks first, then sink
    for module_id in [
        combined.monitor_loopback_id,
        combined.input_loopback_id,
        combined.sink_id,
    ]:
        result = subprocess.run(
            ["pactl", "unload-module", str(module_id)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.warning(f"Failed to unload module {module_id}: {result.stderr}")
        else:
            logger.debug(f"Unloaded module {module_id}")

    logger.info("Combined sink cleanup complete")
