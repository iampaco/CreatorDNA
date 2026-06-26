from pathlib import Path
import subprocess

import pytest

from workers.services.ffmpeg import FfmpegError, compute_frame_timestamps, extract_frames_at_timestamps, probe_duration

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
SAMPLE_VIDEO = FIXTURE_DIR / "sample.webm"


def _ensure_sample_video() -> Path:
    if SAMPLE_VIDEO.exists():
        return SAMPLE_VIDEO
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=320x240:d=6",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:duration=6",
        "-shortest",
        "-c:v",
        "libvpx-vp9",
        "-c:a",
        "libopus",
        str(SAMPLE_VIDEO),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"could not generate sample video: {result.stderr}")
    return SAMPLE_VIDEO


def test_compute_frame_timestamps_covers_hook_middle_end() -> None:
    timestamps = compute_frame_timestamps(60.0)
    assert timestamps[0] <= 5.0
    assert any(25 <= t <= 35 for t in timestamps)
    assert any(t >= 55 for t in timestamps)


def test_probe_and_extract_frames_from_sample_video(tmp_path: Path) -> None:
    sample = _ensure_sample_video()

  duration = probe_duration(sample)
  timestamps = compute_frame_timestamps(duration, max_frames=4)
  frames = extract_frames_at_timestamps(sample, tmp_path / "frames", timestamps)
  assert len(frames) == len(timestamps)
  for frame in frames:
      assert frame.path.exists()
      assert frame.path.stat().st_size > 0


def test_probe_duration_rejects_invalid_file(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.webm"
    bad_file.write_text("not a video")
    with pytest.raises(FfmpegError):
        probe_duration(bad_file)
