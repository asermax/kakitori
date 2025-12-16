import shutil
import signal
import subprocess
from pathlib import Path


def start_recording(
    source: str,
    output_path: Path,
) -> subprocess.Popen:
    """Start ffmpeg recording process from a single PulseAudio source.

    Args:
        source: PulseAudio source name (e.g., combined sink monitor)
        output_path: Path for output file

    Returns:
        Running ffmpeg subprocess
    """
    cmd = [
        "ffmpeg",
        "-thread_queue_size",
        "1024",
        "-f",
        "pulse",
        "-i",
        source,
        "-c:a",
        "libopus",
        str(output_path),
    ]

    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def stop_recording(process: subprocess.Popen) -> None:
    """Gracefully stop the ffmpeg recording process.

    Args:
        process: Running ffmpeg subprocess
    """
    try:
        process.stdin.write(b"q")
        process.stdin.flush()
        process.stdin.close()
    except (BrokenPipeError, ValueError):
        pass


def record_audio(
    source: str,
    output_path: Path,
) -> bool:
    """Execute the full recording workflow with signal handling.

    Args:
        source: PulseAudio source name (e.g., combined sink monitor)
        output_path: Final output path

    Returns:
        True if recording completed successfully, False otherwise
    """
    temp_path = Path("/tmp") / f"{output_path.stem}_temp{output_path.suffix}"

    process = start_recording(source, temp_path)

    interrupted = False

    def handle_interrupt(signum, frame):
        nonlocal interrupted

        if interrupted:
            return

        interrupted = True
        stop_recording(process)

    signal.signal(signal.SIGINT, handle_interrupt)

    try:
        process.wait()
    except KeyboardInterrupt:
        pass

    if not temp_path.exists():
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(temp_path), str(output_path))

    return True
