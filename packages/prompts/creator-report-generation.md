# Creator Report Generation

Generate a creator-level report from **aggregated statistics** and video-level structured analyses. Do not paste raw transcripts.

## Input

You receive:
- `creatorName` — display name if available
- `aggregatedStatistics` — hook/topic/phrase distributions, visual patterns (shot type, subtitle position/style, B-roll usage), templates, video summaries (no full transcripts)

## Rules

1. Focus on **structure, patterns, and method** — not script cloning.
2. Use statistics to infer positioning, hook formulas, speech style, shooting patterns, and subtitle/editing consistency.
3. `reusableTemplates` should describe structural formulas (e.g. "反常识 → 误区 → 方法 → 总结"), not copied sentences.
4. Write `reportMarkdown` in Chinese as a readable creator intelligence report with sections:
   - 内容定位
   - 目标受众
   - 话题选择模式
   - 开头 Hook 公式
   - 视频结构模式
   - 表达风格
   - 拍摄与呈现
   - 字幕与剪辑风格
   - 可复用内容公式
   - 策略建议

## Output JSON

Return a JSON object with:

- `reportMarkdown` (string): user-facing markdown report
- `reportJson` (object) with minimum keys:
  - `positioning` (string)
  - `hookPatterns` (array)
  - `speechStyle` (object)
  - `shootingStyle` (object) — include `dominantStyle`, `shotType`, `cameraPattern`, `backgroundPattern`
  - `subtitleEditingStyle` (object) — include `position`, `style`, `consistency`, `bRollUsage`, `visualDensity`
  - `reusableTemplates` (array of strings)

Optional additional keys: `topicPatterns`, `targetAudience`, `recommendations`.

Focus on structure and patterns for original creation — not script cloning.
