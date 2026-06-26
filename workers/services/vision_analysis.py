import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parents[2] / "packages" / "prompts" / "frame-visual-analysis.md"

FRAME_REQUIRED = [
    "frameTime",
    "shotType",
    "cameraAngle",
    "composition",
    "background",
    "subtitleVisible",
    "subtitlePosition",
    "subtitleStyle",
    "visualElements",
    "bRoll",
]

SUMMARY_REQUIRED = [
    "dominantFormat",
    "dominantShotType",
    "dominantCameraAngle",
    "dominantComposition",
    "dominantBackground",
    "subtitleConsistency",
    "dominantSubtitlePosition",
    "dominantSubtitleStyle",
    "bRollUsage",
    "visualDensity",
    "shootingStyleHint",
]


def load_frame_visual_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _validate_frame(frame: dict, index: int) -> None:
    missing = [field for field in FRAME_REQUIRED if field not in frame]
    if missing:
        raise ValueError(f"frame {index} missing fields: {', '.join(missing)}")
    if not isinstance(frame["subtitleVisible"], bool):
        raise ValueError(f"frame {index} subtitleVisible must be boolean")
    if not isinstance(frame["bRoll"], bool):
        raise ValueError(f"frame {index} bRoll must be boolean")
    if not isinstance(frame["visualElements"], list):
        raise ValueError(f"frame {index} visualElements must be a list")


def parse_visual_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    data = json.loads(text)
    if "frames" not in data or "summary" not in data:
        raise ValueError("missing frames or summary")
    if not isinstance(data["frames"], list) or not data["frames"]:
        raise ValueError("frames must be a non-empty list")
    if not isinstance(data["summary"], dict):
        raise ValueError("summary must be an object")

    for index, frame in enumerate(data["frames"]):
        if not isinstance(frame, dict):
            raise ValueError(f"frame {index} must be an object")
        _validate_frame(frame, index)

    missing_summary = [field for field in SUMMARY_REQUIRED if field not in data["summary"]]
    if missing_summary:
        raise ValueError(f"summary missing fields: {', '.join(missing_summary)}")
    return data
