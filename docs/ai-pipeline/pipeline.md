# AI Pipeline

## Overview

```txt
Metadata (browser) → Media upload → Preprocess → ASR → [Vision] → Structure analysis → [Aggregation] → Report
```

Intermediate steps output **structured JSON**. Final report may be Markdown + JSON.

## Stage 1 — Metadata

**Source:** Extension content script (visible DOM only).

Fields: platform, creator, video URL, title, description, cover, metrics, publish time, duration.

## Stage 2 — Audio Pipeline

```bash
ffmpeg -i input.webm -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

**ASR output** → `transcripts` table:

```json
{
  "video_id": "video_001",
  "duration": 58.4,
  "language": "zh",
  "segments": [{ "start": 0.0, "end": 3.2, "text": "..." }],
  "words": []
}
```

**Speech style signals** (computed or inferred): speed, sentence length, pauses, repeated phrases, hook type, tone, rhetorical style.

## Visual Pipeline

### Frame extraction

```bash
ffmpeg -i input.webm -vf fps=1/3 frames/frame_%04d.jpg
```

Prioritize: first 0–5s, middle, final 3–5s.

### Per-frame analysis

Prompt: `packages/prompts/frame-visual-analysis.md`

Expected fields: shot type, camera angle, composition, background, subtitle visibility/position/style, visual elements, B-roll flag.

### Summary

Roll up frame analyses into `visual_analyses.summary` JSONB.

## Stage 3 — Video Structure Analysis

Prompt: `packages/prompts/video-structure-analysis.md`

**Inputs:** transcript segments, metadata, optional vision summary.

**Output** → `video_style_analyses`:

- `hook_type`, `hook_text`, `topic_category`, `target_audience`
- `content_structure[]`, `emotional_tone`, `common_phrases`
- `ending_type`, `shooting_style`, `reusable_template`

Validate JSON before save. Store `raw_analysis` for debugging.

## Stage 4 — Creator Aggregation

**Do not** concatenate all transcripts into one LLM prompt.

1. Collect N validated `video_style_analyses`
2. Compute aggregates: top categories, hook distribution, phrase frequency, visual consistency
3. Pass **statistics + representative examples** to `creator-report-generation.md`

## Stage 5 — Report Generation

Prompt: `packages/prompts/creator-report-generation.md`

Report sections:

1. Creator positioning
2. Target audience
3. Topic selection pattern
4. Title and hook formula
5. Video structure pattern
6. Speaking style
7. Shooting style
8. Subtitle and editing style
9. High-performing video pattern
10. Reusable content formula
11. Original script templates (structure-inspired)
12. Strategic recommendations

## Prompt Rules

- All prompts under `packages/prompts/`
- Request JSON for intermediate steps
- Version prompts in filename or frontmatter
- Log `prompt_version` and `model` with each output

## Related

- [AGENTS.md — AI Pipeline Design](../../AGENTS.md#ai-pipeline-design)
- [Compliance](../compliance/compliance.md)
