import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class FfmpegError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExtractedFrame:
    timestamp: float
    path: Path


def probe_duration(input_path: Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(input_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffprobe failed: %s", result.stderr)
        raise FfmpegError(result.stderr or "ffprobe failed")
    payload = json.loads(result.stdout or "{}")
    duration = float(payload.get("format", {}).get("duration") or 0)
    if duration <= 0:
        raise FfmpegError("could not determine video duration")
    return duration


def compute_frame_timestamps(duration: float, *, max_frames: int = 8) -> list[float]:
    """Pick sparse timestamps covering hook (0–5s), middle, and ending."""
    if duration <= 0:
        return [0.0, 1.0, 2.0]

    candidates: set[float] = set()
    hook_points = [0.5, 2.0, min(4.0, duration * 0.08)]
    for point in hook_points:
        if 0 <= point < duration:
            candidates.add(round(point, 2))

    candidates.add(round(duration / 2, 2))

    ending_points = [duration - 4.0, duration - 2.0, max(duration - 0.5, 0.0)]
    for point in ending_points:
        if 0 < point < duration:
            candidates.add(round(point, 2))

    timestamps = sorted(candidates)
    if len(timestamps) > max_frames:
        step = max(1, len(timestamps) // max_frames)
        timestamps = timestamps[::step][:max_frames]
    return timestamps


def extract_audio_wav(input_path: Path, output_path: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg failed: %s", result.stderr)
        raise FfmpegError(result.stderr or "ffmpeg failed")


def extract_frame_at_timestamp(input_path: Path, timestamp: float, output_path: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{timestamp:.3f}",
        "-i",
        str(input_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg frame extract failed at %s: %s", timestamp, result.stderr)
        raise FfmpegError(result.stderr or "ffmpeg frame extract failed")


def extract_frames_at_timestamps(
    input_path: Path,
    output_dir: Path,
    timestamps: list[float],
) -> list[ExtractedFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)
    frames: list[ExtractedFrame] = []
    for index, timestamp in enumerate(timestamps, start=1):
        output_path = output_dir / f"frame_{index:04d}.jpg"
        extract_frame_at_timestamp(input_path, timestamp, output_path)
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise FfmpegError(f"frame not written at timestamp {timestamp}")
        frames.append(ExtractedFrame(timestamp=timestamp, path=output_path))
    return frames
