# Video Structure Analysis

Analyze a short-video transcript and metadata. Return **structured JSON only** (no prose).

You are helping creators learn content strategy from structural patterns. Do not copy wording verbatim; summarize structure, hook patterns, and reusable formulas.

## Input

You receive:

- `title` — video title if available
- `transcript` — ASR transcript text

## Output JSON schema

Return a single JSON object with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `hookType` | string | e.g. 反常识开头 |
| `hookText` | string | Opening hook sentence (summarized, not copied verbatim) |
| `topicCategory` | string | Content category |
| `targetAudience` | string[] | Audience tags |
| `contentStructure` | `{part, description}[]` | Hook → body → ending |
| `emotionalTone` | string | Tone description |
| `commonPhrases` | string[] | Recurring phrases (structural, not identity cloning) |
| `endingType` | string | Ending pattern |
| `shootingStyle` | string | Visual/speech style hint from transcript cues |
| `reusableTemplate` | string | Structural formula (not a script clone) |

## Rules

- Output valid JSON only.
- All string values in Chinese when the source is Chinese.
- Focus on structure and method, not impersonation.
- If transcript is short or noisy, infer conservatively and say so in `emotionalTone`.

## Example

```json
{
  "hookType": "反常识开头",
  "hookText": "很多人以为做内容靠灵感，其实靠结构。",
  "topicCategory": "内容创作方法论",
  "targetAudience": ["短视频创作者", "个人 IP", "创业者"],
  "contentStructure": [
    { "part": "开头", "description": "提出常见误区并制造认知冲突" },
    { "part": "正文", "description": "解释爆款内容背后的结构规律" },
    { "part": "结尾", "description": "用一句方法论总结并引导关注" }
  ],
  "emotionalTone": "坚定、教学式、轻微制造焦虑",
  "commonPhrases": ["本质上", "你会发现", "说白了"],
  "endingType": "观点总结 + 关注引导",
  "shootingStyle": "正面口播 + 大字幕",
  "reusableTemplate": "反常识判断 → 常见误区 → 方法解释 → 一句话总结"
}
```
