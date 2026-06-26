import json

import pytest

from workers.services.vision_analysis import parse_visual_json


def _sample_visual_payload() -> dict:
    return {
        "frames": [
            {
                "frameTime": 2.0,
                "shotType": "真人口播",
                "cameraAngle": "正面",
                "composition": "半身近景",
                "background": "室内书桌",
                "subtitleVisible": True,
                "subtitlePosition": "底部居中",
                "subtitleStyle": "白色大字，黑色描边",
                "visualElements": ["人物", "字幕"],
                "bRoll": False,
            }
        ],
        "summary": {
            "dominantFormat": "真人口播",
            "dominantShotType": "真人口播",
            "dominantCameraAngle": "正面",
            "dominantComposition": "半身近景",
            "dominantBackground": "室内书桌",
            "subtitleConsistency": "全程一致",
            "dominantSubtitlePosition": "底部居中",
            "dominantSubtitleStyle": "白色大字，黑色描边",
            "bRollUsage": "无B-roll",
            "visualDensity": "简洁口播",
            "shootingStyleHint": "正面口播 + 底部居中大字幕",
        },
    }


def test_parse_visual_json_accepts_fenced_json() -> None:
    payload = _sample_visual_payload()
    raw = "```json\n" + json.dumps(payload, ensure_ascii=False) + "\n```"
    parsed = parse_visual_json(raw)
    assert parsed["summary"]["dominantSubtitlePosition"] == "底部居中"


def test_parse_visual_json_rejects_missing_summary_fields() -> None:
    payload = _sample_visual_payload()
    del payload["summary"]["shootingStyleHint"]
    with pytest.raises(ValueError):
        parse_visual_json(json.dumps(payload, ensure_ascii=False))
