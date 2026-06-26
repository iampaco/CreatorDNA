# Architecture Overview

## System Layers

```txt
┌─────────────────────────────────────────────────────────┐
│  Browser Extension (WXT / React / MV3)                  │
│  content · background · popup · sidepanel · offscreen   │
└──────────────────────────┬──────────────────────────────┘
                           │ Platform Adapter Layer
┌──────────────────────────▼──────────────────────────────┐
│  API Gateway (FastAPI)                                  │
│  tasks · uploads · progress · reports                   │
└──────────────────────────┬──────────────────────────────┘
                           │ Task Queue (Redis + Celery/BullMQ)
┌──────────────────────────▼──────────────────────────────┐
│  AI Processing Workers                                  │
│  preprocess · ASR · vision · style · report             │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  PostgreSQL + Object Storage (R2/S3)                    │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Extension Side Panel / Web Dashboard (optional)        │
└─────────────────────────────────────────────────────────┘
```

## Separation of Concerns

| Layer | Owns | Must not own |
|-------|------|--------------|
| Content script | DOM observation, metadata extraction | AI inference, media encoding |
| Background SW | State, API calls, capture orchestration | Heavy processing |
| Offscreen doc | MediaRecorder, chunk upload | Business logic |
| Platform adapters | Per-site detection and extraction | Shared UI |
| API | Auth, validation, enqueue, CRUD | ffmpeg, model calls |
| Workers | Media + AI pipelines | Browser APIs |
| Packages | Types, prompts, shared utils | App-specific wiring |

## Key Modules

### Browser Extension

- **content.ts** — inject adapter, observe page, send normalized events
- **background.ts** — task lifecycle, tab capture stream ID, backend communication
- **offscreen/** — user-initiated recording only
- **sidepanel/** — MVP report UI
- **platform-adapters/** — `PlatformAdapter` interface per platform

### Backend API

- Routers: creator analysis, video upload, task progress, reports
- Services: task creation, storage URLs, report retrieval
- Schemas: Pydantic request/response models aligned with `packages/shared-types`

### Workers

| Worker | Input | Output |
|--------|-------|--------|
| `video_preprocess_worker` | Raw media blob | Normalized audio, frames |
| `asr_worker` | Audio WAV | Transcript JSON |
| `vision_worker` | Frame images | Per-frame + summary JSON |
| `style_analysis_worker` | Transcript + metadata (+ vision) | Video style JSON |
| `report_worker` | N video analyses | Creator report MD + JSON |

### Shared Packages

- `shared-types` — Creator, Video, Task, Report, Platform enums
- `prompts` — versioned markdown prompts for each AI step
- `ai-clients` — provider wrappers with logging
- `platform-core` — adapter interface and detection helpers

## Job Types

```txt
ANALYZE_CREATOR
DISCOVER_VIDEOS
ANALYZE_VIDEO
EXTRACT_AUDIO
TRANSCRIBE_AUDIO
EXTRACT_FRAMES
ANALYZE_FRAMES
ANALYZE_VIDEO_STRUCTURE
GENERATE_CREATOR_REPORT
EXPORT_REPORT
```

Jobs should be idempotent; retries must not duplicate records.

## Aggregation Strategy

Do **not** send raw transcripts of many videos to one LLM call.

```txt
Per video → structured video_style_analysis (JSON)
         → aggregate statistics (hooks, topics, phrases, visuals)
         → final report generation (prose + structured JSON)
```

## Related Docs

- [Monorepo Structure](./monorepo-structure.md)
- [Data Flow](./data-flow.md)
- [AI Pipeline](../ai-pipeline/pipeline.md)
- [API Reference](../api/api.md)
