# Video Structure Analysis

> Placeholder — full prompt content in Phase 1+ (P1-08).

Analyze a short-video transcript and metadata. Return **structured JSON only** (no prose).

## Output fields

| Field | Type | Description |
|-------|------|-------------|
| `hookType` | string | e.g. 反常识开头 |
| `hookText` | string | Opening hook sentence |
| `topicCategory` | string | Content category |
| `targetAudience` | string[] | Audience tags |
| `contentStructure` | `{part, description}[]` | Hook → body → ending |
| `emotionalTone` | string | Tone description |
| `commonPhrases` | string[] | Recurring phrases |
| `endingType` | string | Ending pattern |
| `shootingStyle` | string | Visual/speech style hint |
| `reusableTemplate` | string | Structural formula (not verbatim script) |

See [AGENTS.md](../../AGENTS.md) for example JSON.
