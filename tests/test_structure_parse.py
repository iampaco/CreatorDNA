import json

import pytest

from workers.services.structure_analysis import parse_structure_json


def test_parse_structure_json_accepts_fenced_json() -> None:
    payload = {
        "hookType": "反常识开头",
        "hookText": "测试",
        "topicCategory": "测试",
        "targetAudience": ["创作者"],
        "contentStructure": [{"part": "开头", "description": "引出话题"}],
        "emotionalTone": "教学式",
        "commonPhrases": ["本质上"],
        "endingType": "总结",
        "shootingStyle": "口播",
        "reusableTemplate": "A → B",
    }
    raw = "```json\n" + json.dumps(payload, ensure_ascii=False) + "\n```"
    parsed = parse_structure_json(raw)
    assert parsed["hookType"] == "反常识开头"


def test_parse_structure_json_rejects_missing_fields() -> None:
    with pytest.raises(ValueError):
        parse_structure_json('{"hookType":"x"}')
