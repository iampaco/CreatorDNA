import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class FfmpegError(RuntimeError):
    pass


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
