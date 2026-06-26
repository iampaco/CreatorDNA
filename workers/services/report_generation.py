import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPT_PATH = (
    Path(__file__).resolve().parents[2] / "packages" / "prompts" / "creator-report-generation.md"
)


class ReportGenerationError(RuntimeError):
    pass


def load_creator_report_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def parse_report_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    data = json.loads(text)
    required = ["positioning", "hookPatterns", "speechStyle", "shootingStyle", "reusableTemplates"]
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError(f"missing fields: {', '.join(missing)}")
    if not isinstance(data["hookPatterns"], list):
        raise ValueError("hookPatterns must be a list")
    if not isinstance(data["reusableTemplates"], list):
        raise ValueError("reusableTemplates must be a list")
    if not isinstance(data["speechStyle"], dict):
        raise ValueError("speechStyle must be an object")
    if not isinstance(data["shootingStyle"], dict):
        raise ValueError("shootingStyle must be an object")
    return data


def _mock_report(aggregated: dict, creator_name: str | None) -> dict:
    name = creator_name or "该创作者"
    top_hook = aggregated.get("hookTypeDistribution", [{}])[0].get("value", "反常识开头")
    top_topic = aggregated.get("topicCategoryDistribution", [{}])[0].get("value", "内容创作")
    templates = [t.get("value") for t in aggregated.get("reusableTemplates", [])[:3]]
    phrases = [p.get("value") for p in aggregated.get("commonPhrases", [])[:5]]

    report_json = {
        "positioning": f"{name} 专注于 {top_topic} 类内容，以结构化表达帮助观众建立认知。",
        "hookPatterns": aggregated.get("hookTypeDistribution", []),
        "speechStyle": {
            "tone": aggregated.get("emotionalToneDistribution", [{}])[0].get("value", "教学式"),
            "commonPhrases": phrases,
            "rhetoricalStyle": "方法论讲解",
        },
        "shootingStyle": {
            "dominantStyle": aggregated.get("shootingStyleDistribution", [{}])[0].get("value", "正面口播"),
            "subtitlePattern": "大字幕强调关键观点",
        },
        "reusableTemplates": templates or ["反常识判断 → 误区拆解 → 方法解释 → 总结引导"],
        "topicPatterns": aggregated.get("topicCategoryDistribution", []),
        "targetAudience": aggregated.get("targetAudience", []),
    }

    markdown = f"""# {name} 创作者风格报告

## 内容定位
{report_json["positioning"]}

## 开头 Hook 模式
最常使用的开头类型：**{top_hook}**

## 话题选择
{", ".join(t.get("value", "") for t in aggregated.get("topicCategoryDistribution", [])[:5]) or "暂无足够样本"}

## 表达风格
- 情绪基调：{report_json["speechStyle"]["tone"]}
- 常用表达：{", ".join(phrases) or "暂无"}

## 拍摄与呈现
{report_json["shootingStyle"]["dominantStyle"]}

## 可复用内容公式
{chr(10).join(f"- {t}" for t in report_json["reusableTemplates"])}

---
*本报告基于结构分析生成，用于学习创作方法，而非复制具体文案。*
"""
    return {"reportMarkdown": markdown, "reportJson": report_json}


def generate_creator_report(
    *,
    aggregated: dict,
    creator_name: str | None,
) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY missing; using dev mock creator report")
        return _mock_report(aggregated, creator_name)

    from openai import OpenAI

    prompt = load_creator_report_prompt()
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    user_payload = {
        "creatorName": creator_name or "",
        "aggregatedStatistics": aggregated,
        "instructions": (
            "Generate a creator-level report from aggregated statistics only. "
            "Do not invent verbatim scripts. Focus on patterns for original creation."
        ),
    }

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": (
                    "Return a JSON object with exactly these keys: "
                    "reportMarkdown (string, markdown prose), reportJson (object with "
                    "positioning, hookPatterns, speechStyle, shootingStyle, reusableTemplates).\n\n"
                    f"{json.dumps(user_payload, ensure_ascii=False)}"
                ),
            },
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or ""
    parsed = json.loads(content)
    if "reportMarkdown" not in parsed or "reportJson" not in parsed:
        raise ReportGenerationError("LLM response missing reportMarkdown or reportJson")
    report_json = parse_report_json(json.dumps(parsed["reportJson"], ensure_ascii=False))
    return {
        "reportMarkdown": str(parsed["reportMarkdown"]),
        "reportJson": report_json,
    }
