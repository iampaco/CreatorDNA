# Data Flow

## Single-Video Analysis (MVP Path)

```mermaid
sequenceDiagram
  participant User
  participant Ext as Extension
  participant API as API Gateway
  participant Q as Task Queue
  participant W as Workers
  participant DB as PostgreSQL + Storage

  User->>Ext: Open video page, click Analyze
  Ext->>Ext: tabCapture (user consent)
  Ext->>Offscreen: Record segment (30-60s)
  Offscreen->>API: POST /api/videos/upload
  API->>DB: Store media + video metadata
  API->>Q: ANALYZE_VIDEO
  Q->>W: EXTRACT_AUDIO → TRANSCRIBE_AUDIO
  W->>DB: Save transcript
  Q->>W: ANALYZE_VIDEO_STRUCTURE
  W->>DB: Save video_style_analysis
  Ext->>API: GET /api/tasks/:taskId (poll)
  Ext->>API: GET report for video
  Ext->>User: Render in side panel
```

## Creator Batch Analysis (Phase 2)

```mermaid
sequenceDiagram
  participant User
  participant Ext as Extension
  participant API as API Gateway
  participant Q as Task Queue
  participant W as Workers

  User->>Ext: Open creator profile, select N videos
  Ext->>Ext: extractVideoList(limit)
  Ext->>API: POST /api/creator-analysis
  API->>Q: ANALYZE_CREATOR
  loop Each video
    Q->>W: Per-video pipeline (as above)
  end
  Q->>W: GENERATE_CREATOR_REPORT
  W->>W: Aggregate stats → LLM report
  Ext->>User: Creator report in side panel
```

## Metadata Extraction (Browser-Side)

Collected from visible DOM / page context before capture:

- Platform, creator URL, display name, handle
- Video URL, title, description, cover
- Like / comment / collect counts (if visible)
- Publish time, duration (if available)

Sent to background → API as normalized `CreatorVideoMeta` / `CreatorProfile`.

## Worker Pipeline Stages

| Stage | Tooling | Stored in |
|-------|---------|-----------|
| Preprocess | ffmpeg | Object storage (temp) |
| ASR | Whisper / OpenAI STT | `transcripts` |
| Frame extract | ffmpeg (sparse fps) | Object storage |
| Vision | GPT/Gemini vision | `visual_analyses` |
| Structure | LLM + prompt | `video_style_analyses` |
| Report | LLM + aggregated stats | `creator_reports` |

## Progress Reporting

`GET /api/tasks/:taskId` returns:

- `status`, `progress` (0-100)
- `currentStep` (human-readable)
- `finishedVideos` / `totalVideos` for batch jobs

Extension polls or uses SSE/WebSocket (future) to update UI.

## Failure Points

| Failure | User-facing behavior |
|---------|---------------------|
| Unsupported platform | Explain supported sites |
| No videos found | Suggest scroll or manual selection |
| Tab capture denied | Instructions to grant permission |
| Upload failure | Retry with clear error |
| ASR / vision / LLM failure | Partial report or step retry |
| User cancel | Stop recording, cancel queued jobs |

See [AGENTS.md](../../AGENTS.md#error-handling) for full list.
