import logging
import os
import time
from pathlib import Path

from workers.services.quota import check_and_increment, log_ai_usage

logger = logging.getLogger(__name__)


class AsrError(RuntimeError):
    pass


def transcribe_audio(wav_path: Path) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY missing; using dev mock transcript")
        return {
            "language": "zh",
            "full_text": "很多人做内容最大的问题，不是不会拍，而是没有结构。",
            "segments": [
                {"start": 0.0, "end": 3.2, "text": "很多人做内容最大的问题，不是不会拍，而是没有结构。"}
            ],
            "asr_model": "dev-mock-whisper",
        }

    check_and_increment("TRANSCRIBE_AUDIO")
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_ASR_MODEL", "whisper-1")
    started = time.perf_counter()
    with wav_path.open("rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="verbose_json",
        )

    full_text = getattr(response, "text", "") or ""
    segments = []
    for segment in getattr(response, "segments", []) or []:
        segments.append(
            {
                "start": float(getattr(segment, "start", 0.0)),
                "end": float(getattr(segment, "end", 0.0)),
                "text": getattr(segment, "text", ""),
            }
        )

    duration_ms = int((time.perf_counter() - started) * 1000)
    log_ai_usage(step="TRANSCRIBE_AUDIO", model=model, duration_ms=duration_ms)

    return {
        "language": getattr(response, "language", None) or "zh",
        "full_text": full_text,
        "segments": segments,
        "asr_model": model,
    }
