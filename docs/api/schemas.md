# Schema Reference

Index of core data contracts. Canonical SQL and JSON examples in [AGENTS.md](../../AGENTS.md#database-design). TypeScript definitions live in `packages/shared-types/` (P0-02); Pydantic mirrors in `apps/api/schemas/`.

## Platform & Page

### `PlatformPageDetection`

| Field | Type | Description |
|-------|------|-------------|
| `platform` | `"douyin"` | Platform identifier |
| `pageType` | `"video" \| "creator" \| "unknown"` | Current page classification |
| `url` | `string` | Current page URL |

### `CreatorProfile`

| Field | Type | Description |
|-------|------|-------------|
| `platform` | `string` | e.g. `douyin` |
| `displayName` | `string?` | Visible name |
| `username` | `string?` | Handle if visible |
| `profileUrl` | `string` | Canonical profile URL |
| `avatarUrl` | `string?` | Avatar image URL |

### `CreatorVideoMeta`

| Field | Type | Description |
|-------|------|-------------|
| `platform` | `string` | e.g. `douyin` |
| `videoUrl` | `string` | Canonical video URL |
| `platformVideoId` | `string?` | Platform-native ID |
| `title` | `string?` | Visible title |
| `description` | `string?` | Visible description |
| `coverUrl` | `string?` | Thumbnail |
| `likeCount` | `number?` | If visible |
| `commentCount` | `number?` | If visible |
| `collectCount` | `number?` | If visible |
| `publishTime` | `string?` | ISO 8601 if parseable |
| `durationSeconds` | `number?` | If available |

## Tasks

### `AnalysisTask` / `TaskProgress`

| Field | Type | Description |
|-------|------|-------------|
| `taskId` | `string` | UUID |
| `status` | `"queued" \| "processing" \| "completed" \| "failed" \| "cancelled"` | |
| `progress` | `number` | 0–100 |
| `currentStep` | `string?` | Human-readable step |
| `finishedVideos` | `number?` | Batch only |
| `totalVideos` | `number?` | Batch only |
| `error` | `string?` | On failure |

## Transcript (ASR output)

| Field | Type | Description |
|-------|------|-------------|
| `videoId` | `string` | FK to videos |
| `language` | `string` | e.g. `zh` |
| `fullText` | `string` | Concatenated transcript |
| `segments` | `Array<{start, end, text}>` | Timed segments |
| `words` | `array` | Optional word-level |
| `asrModel` | `string` | Provider + model name |

## Video Style Analysis

| Field | Type | Description |
|-------|------|-------------|
| `hookType` | `string` | e.g. 反常识开头 |
| `hookText` | `string` | Opening hook text |
| `topicCategory` | `string` | Content category |
| `targetAudience` | `string[]` | Audience tags |
| `contentStructure` | `Array<{part, description}>` | Structural breakdown |
| `emotionalTone` | `string` | Tone description |
| `commonPhrases` | `string[]` | Recurring phrases |
| `endingType` | `string` | Ending pattern |
| `shootingStyle` | `string` | Visual/speech combined |
| `reusableTemplate` | `string` | Structural formula |

## Visual Analysis

| Field | Type | Description |
|-------|------|-------------|
| `frames` | `JSONB` | Per-frame analysis array (`frameTime`, `shotType`, `subtitlePosition`, etc.) |
| `summary` | `JSONB` | Rolled-up visual summary (`dominantShotType`, `dominantSubtitlePosition`, `shootingStyleHint`, etc.) |
| `visionModel` | `string` | Model identifier |

`GET /api/videos/:videoId/analysis` returns `visualAnalysis` alongside `analysis` and `transcript`.

## Creator Report

| Field | Type | Description |
|-------|------|-------------|
| `creatorId` | `string` | UUID |
| `sampleVideoCount` | `number` | Videos analyzed |
| `reportMarkdown` | `string` | User-facing report |
| `reportJson` | `object` | Structured sections |

### `reportJson` sections (minimum)

`positioning`, `hookPatterns`, `speechStyle`, `shootingStyle`, `subtitleEditingStyle`, `reusableTemplates`

## API Error Shape

```json
{
  "error": "capture_denied",
  "message": "Human-readable description"
}
```

Common codes: `unsupported_platform`, `no_videos_found`, `upload_failed`, `asr_failed`, `vision_failed`, `llm_parse_failed`, `rate_limited`, `unauthorized`

## Related

- [api.md](./api.md)
- [AGENTS.md](../../AGENTS.md)
