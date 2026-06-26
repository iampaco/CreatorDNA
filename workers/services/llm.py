import json
import logging
import os

from workers.services.structure_analysis import load_video_structure_prompt, parse_structure_json

logger = logging.getLogger(__name__)


class LlmError(RuntimeError):
    pass


def analyze_structure(
    *,
    transcript_text: str,
    title: str | None,
    visual_summary: dict | None = None,
) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = load_video_structure_prompt()
    user_payload: dict = {
        "title": title or "",
        "transcript": transcript_text,
    }
    if visual_summary:
        user_payload["visualSummary"] = visual_summary

    if not api_key:
        logger.warning("OPENAI_API_KEY missing; using dev mock structure analysis")
        shooting_style = "正面口播 + 大字幕"
        if visual_summary and visual_summary.get("shootingStyleHint"):
            shooting_style = str(visual_summary["shootingStyleHint"])
        return {
            "hookType": "反常识开头",
            "hookText": transcript_text[:40] or "很多人以为做内容靠灵感，其实靠结构。",
            "topicCategory": "内容创作方法论",
            "targetAudience": ["短视频创作者", "个人 IP"],
            "contentStructure": [
                {"part": "开头", "description": "提出常见误区并制造认知冲突"},
                {"part": "正文", "description": "解释爆款内容背后的结构规律"},
                {"part": "结尾", "description": "用一句方法论总结并引导关注"},
            ],
            "emotionalTone": "坚定、教学式",
            "commonPhrases": ["本质上", "你会发现"],
            "endingType": "观点总结 + 关注引导",
            "shootingStyle": shooting_style,
            "reusableTemplate": "反常识判断 → 常见误区 → 方法解释 → 一句话总结",
            "raw_model": "dev-mock-gpt",
        }

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": (
                    "Analyze the following short-video transcript and metadata. "
                    "Return JSON only.\n\n"
                    f"{json.dumps(user_payload, ensure_ascii=False)}"
                ),
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or ""
    parsed = parse_structure_json(content)
    parsed["raw_model"] = model
    return parsed
