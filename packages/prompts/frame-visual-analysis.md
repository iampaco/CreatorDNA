# Frame Visual Analysis

Analyze extracted short-video frames. Return **structured JSON only** (no prose).

You are helping creators learn shooting, subtitle, and editing patterns from visual structure — not copying identity or exact on-screen text.

## Input

You receive:

- `frames` — array of `{ frameTime, imageDescription? }` where `frameTime` is seconds into the video
- Frame images are attached for visual inspection

## Output JSON schema

Return a single JSON object:

| Field | Type | Description |
|-------|------|-------------|
| `frames` | `FrameAnalysis[]` | One entry per input frame (same order) |
| `summary` | `VisualSummary` | Rolled-up patterns across all frames |

### `FrameAnalysis`

| Field | Type | Description |
|-------|------|-------------|
| `frameTime` | number | Seconds (must match input) |
| `shotType` | string | e.g. 真人口播, 屏幕录制, vlog, 混剪 |
| `cameraAngle` | string | e.g. 正面, 侧面, 俯拍 |
| `composition` | string | e.g. 半身近景, 全身远景 |
| `background` | string | e.g. 室内书桌, 户外街道 |
| `subtitleVisible` | boolean | Whether subtitles/captions are visible |
| `subtitlePosition` | string | e.g. 底部居中, 顶部, 无字幕 |
| `subtitleStyle` | string | e.g. 白色大字黑色描边 |
| `visualElements` | string[] | Notable elements: 人物, 字幕, 产品, etc. |
| `bRoll` | boolean | Whether frame is B-roll (not primary talking head) |

### `VisualSummary`

| Field | Type | Description |
|-------|------|-------------|
| `dominantFormat` | string | Primary video format across frames |
| `dominantShotType` | string | Most common shot type |
| `dominantCameraAngle` | string | Most common camera angle |
| `dominantComposition` | string | Most common framing |
| `dominantBackground` | string | Most common background type |
| `subtitleConsistency` | string | e.g. 全程一致, 部分出现, 无字幕 |
| `dominantSubtitlePosition` | string | Most common subtitle position |
| `dominantSubtitleStyle` | string | Most common subtitle style |
| `bRollUsage` | string | e.g. 少量穿插, 无B-roll, 频繁切换 |
| `visualDensity` | string | e.g. 简洁口播, 信息密集, 快节奏剪辑 |
| `shootingStyleHint` | string | One-line shooting + subtitle summary for downstream structure analysis |

## Rules

- Output valid JSON only.
- All string values in Chinese when the video appears Chinese.
- Infer conservatively when frames are blurry or ambiguous.
- Do not transcribe full subtitle text — describe style and position only.
- `frames` length must equal input frame count; `frameTime` must match input.

## Example

```json
{
  "frames": [
    {
      "frameTime": 2.0,
      "shotType": "真人口播",
      "cameraAngle": "正面",
      "composition": "半身近景",
      "background": "室内书桌",
      "subtitleVisible": true,
      "subtitlePosition": "底部居中",
      "subtitleStyle": "白色大字，黑色描边",
      "visualElements": ["人物", "字幕", "桌面"],
      "bRoll": false
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
    "shootingStyleHint": "正面口播 + 底部居中大字幕"
  }
}
```
