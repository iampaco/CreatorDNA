import json
import logging
import os
import time

from workers.services.quota import QuotaExceededError, check_and_increment, log_ai_usage
from workers.services.structure_analysis import load_video_structure_prompt, parse_structure_json

logger = logging.getLogger(__name__)


class LlmError(RuntimeError):
    pass


# Re-export for callers
QuotaExceeded = QuotaExceededError


def _llm_config() -> tuple[str | None, str | None, str]:
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL")
    model = os.getenv("LLM_CHAT_MODEL") or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    return api_key, base_url, model


def analyze_structure(
    *,
    transcript_text: str,
    title: str | None,
    visual_summary: dict | None = None,
) -> dict:
    api_key, base_url, model = _llm_config()
    prompt = load_video_structure_prompt()
    user_payload: dict = {
        "title": title or "",
        "transcript": transcript_text,
    }
    if visual_summary:
        user_payload["visualSummary"] = visual_summary

    if not api_key:
        logger.warning("LLM_API_KEY/OPENAI_API_KEY missing; using dev mock structure analysis")
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

    check_and_increment("ANALYZE_VIDEO_STRUCTURE")
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    started = time.perf_counter()
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
    usage = getattr(response, "usage", None)
    tokens = getattr(usage, "total_tokens", None) if usage else None
    duration_ms = int((time.perf_counter() - started) * 1000)
    log_ai_usage(step="ANALYZE_VIDEO_STRUCTURE", model=model, tokens_used=tokens, duration_ms=duration_ms)
    return parsed
