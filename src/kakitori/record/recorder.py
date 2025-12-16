import shutil
import signal
import subprocess
from pathlib import Path


def start_recording(
    input_source: str,
    monitor_source: str,
    output_path: Path,
) -> subprocess.Popen:
    """Start ffmpeg recording process.

    Args:
        input_source: PulseAudio input source name
        monitor_source: PulseAudio monitor source name
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
        input_source,
        "-thread_queue_size",
        "1024",
        "-f",
        "pulse",
        "-i",
        monitor_source,
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=longest[a]",
        "-map",
        "[a]",
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
    input_source: str,
    monitor_source: str,
    output_path: Path,
) -> bool:
    """Execute the full recording workflow with signal handling.

    Args:
        input_source: PulseAudio input source name
        monitor_source: PulseAudio monitor source name
        output_path: Final output path

    Returns:
        True if recording completed successfully, False otherwise
    """
    temp_path = Path("/tmp") / f"{output_path.stem}_temp{output_path.suffix}"

    process = start_recording(input_source, monitor_source, temp_path)

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
