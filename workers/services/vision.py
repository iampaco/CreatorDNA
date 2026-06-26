import base64
import json
import logging
import os
import time
from pathlib import Path

from workers.services.quota import check_and_increment, log_ai_usage
from workers.services.vision_analysis import load_frame_visual_prompt, parse_visual_json

logger = logging.getLogger(__name__)


class VisionError(RuntimeError):
    pass


def _encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _mock_visual_result(frames: list[dict]) -> dict:
    frame_analyses = []
    for frame in frames:
        frame_analyses.append(
            {
                "frameTime": frame["frameTime"],
                "shotType": "真人口播",
                "cameraAngle": "正面",
                "composition": "半身近景",
                "background": "室内场景",
                "subtitleVisible": True,
                "subtitlePosition": "底部居中",
                "subtitleStyle": "白色大字，黑色描边",
                "visualElements": ["人物", "字幕"],
                "bRoll": False,
            }
        )
    return {
        "frames": frame_analyses,
        "summary": {
            "dominantFormat": "真人口播",
            "dominantShotType": "真人口播",
            "dominantCameraAngle": "正面",
            "dominantComposition": "半身近景",
            "dominantBackground": "室内场景",
            "subtitleConsistency": "全程一致",
            "dominantSubtitlePosition": "底部居中",
            "dominantSubtitleStyle": "白色大字，黑色描边",
            "bRollUsage": "无B-roll",
            "visualDensity": "简洁口播",
            "shootingStyleHint": "正面口播 + 底部居中大字幕",
        },
        "raw_model": "dev-mock-vision",
    }


def analyze_frames(*, frame_paths: list[Path], timestamps: list[float]) -> dict:
    if len(frame_paths) != len(timestamps):
        raise VisionError("frame_paths and timestamps length mismatch")
    if not frame_paths:
        raise VisionError("no frames to analyze")

    frame_inputs = [{"frameTime": ts} for ts in timestamps]
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY missing; using dev mock vision analysis")
        return _mock_visual_result(frame_inputs)

    check_and_increment("ANALYZE_FRAMES")
    from openai import OpenAI

    prompt = load_frame_visual_prompt()
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_VISION_MODEL", os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"))
    started = time.perf_counter()

    content: list[dict] = [
        {
            "type": "text",
            "text": (
                "Analyze the attached video frames. Return JSON only.\n\n"
                f"{json.dumps({'frames': frame_inputs}, ensure_ascii=False)}"
            ),
        }
    ]
    for path in frame_paths:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{_encode_image(path)}"},
            }
        )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or ""
    parsed = parse_visual_json(raw)
    parsed["raw_model"] = model
    usage = getattr(response, "usage", None)
    tokens = getattr(usage, "total_tokens", None) if usage else None
    duration_ms = int((time.perf_counter() - started) * 1000)
    log_ai_usage(step="ANALYZE_FRAMES", model=model, tokens_used=tokens, duration_ms=duration_ms)
    return parsed
