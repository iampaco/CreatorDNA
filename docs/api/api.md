# API Reference

Canonical schemas and examples live in [AGENTS.md](../../AGENTS.md#api-design). Field index: [schemas.md](./schemas.md).

## Authentication (P6-01)

All mutating endpoints require authentication in staging/production:

```http
Authorization: Bearer <api_key_or_jwt>
```

- Extension stores API key in `chrome.storage` (user-provided or onboarding)
- `401` if missing/invalid; `403` if key lacks permission
- `/health` remains unauthenticated for load balancers

## Endpoints (Planned)

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| `GET` | `/health` | Liveness | 0 |
| `POST` | `/api/videos/upload` | Upload captured media segment | 1 |
| `GET` | `/api/tasks/:taskId` | Task progress | 1 |
| `GET` | `/api/videos/:videoId/analysis` | Single-video result | 1 |
| `POST` | `/api/creator-analysis` | Start creator batch job | 2 |
| `GET` | `/api/reports/:creatorId` | Creator-level report | 2 |
| `POST` | `/api/reports/:id/export` | Export MD/PDF/JSON | 4 |

## Create Creator Analysis

```http
POST /api/creator-analysis
```

```json
{
  "platform": "douyin",
  "creatorUrl": "https://www.douyin.com/user/example",
  "videoUrls": ["https://www.douyin.com/video/example_001"],
  "sampleSize": 20
}
```

Response: `{ "taskId": "...", "status": "queued" }`

## Upload Video Segment

```http
POST /api/videos/upload
Content-Type: multipart/form-data
```

Fields: `file`, `videoUrl`, `creatorId` (optional)

## Task Progress

```http
GET /api/tasks/:taskId
```

```json
{
  "taskId": "task_123",
  "status": "processing",
  "progress": 65,
  "currentStep": "Analyzing video frames",
  "finishedVideos": 13,
  "totalVideos": 20
}
```

## Error Responses

```json
{
  "error": "rate_limited",
  "message": "Too many requests. Try again later."
}
```

| Code | HTTP | When |
|------|------|------|
| `unauthorized` | 401 | Missing or invalid auth |
| `unsupported_platform` | 400 | Platform not douyin in V1 |
| `no_videos_found` | 400 | Empty video list in batch request |
| `upload_failed` | 500 | Storage or validation error |
| `asr_failed` | 500 | Transcription step failed |
| `vision_failed` | 500 | Vision step failed |
| `llm_parse_failed` | 500 | Invalid LLM JSON |
| `rate_limited` | 429 | Per P6-02 limits |

## Implementation Notes

- All request/response bodies use Pydantic models in `apps/api/schemas/`
- Mirror TypeScript types in `packages/shared-types`
- Return consistent error shape: `{ "error": "code", "message": "..." }`
- Idempotent task creation where `videoUrl` + `creatorId` already exists

## Related

- [Data Flow](../architecture/data-flow.md)
- [Database Design](../../AGENTS.md#database-design)
