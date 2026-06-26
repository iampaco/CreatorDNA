import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parents[2] / "packages" / "prompts" / "video-structure-analysis.md"


def load_video_structure_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def parse_structure_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    data = json.loads(text)
    required = [
        "hookType",
        "hookText",
        "topicCategory",
        "targetAudience",
        "contentStructure",
        "emotionalTone",
        "commonPhrases",
        "endingType",
        "shootingStyle",
        "reusableTemplate",
    ]
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError(f"missing fields: {', '.join(missing)}")
    if not isinstance(data["targetAudience"], list):
        raise ValueError("targetAudience must be a list")
    if not isinstance(data["commonPhrases"], list):
        raise ValueError("commonPhrases must be a list")
    if not isinstance(data["contentStructure"], list):
        raise ValueError("contentStructure must be a list")
    return data
