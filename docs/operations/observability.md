# Observability

## Structured Logging

Every log line in API and workers should include contextual fields where available:

| Field | Description |
|-------|-------------|
| `request_id` | HTTP request correlation (API) |
| `task_id` | Analysis task UUID |
| `creator_id` | Creator UUID |
| `video_id` | Video UUID |
| `step` | Pipeline step name (e.g. `TRANSCRIBE_AUDIO`) |
| `model` | AI model identifier |
| `duration_ms` | Step processing time |
| `error` | Error message on failure |
| `retry_count` | Current retry attempt |

### Log levels

| Level | Use |
|-------|-----|
| `INFO` | Step start/complete, task state transitions |
| `WARNING` | Retryable failures, degraded path |
| `ERROR` | Terminal failures, validation errors |
| `DEBUG` | Local dev only; disable in production |

## Metrics (V1 minimum)

Implement incrementally in P6-03 / P6-11:

| Metric | Type | Labels |
|--------|------|--------|
| `api_requests_total` | counter | `method`, `path`, `status` |
| `task_duration_seconds` | histogram | `step`, `status` |
| `queue_depth` | gauge | `queue_name` |
| `ai_tokens_used` | counter | `provider`, `step` |
| `upload_bytes_total` | counter | — |

Export via Prometheus endpoint or provider-native metrics (optional for V1; logs are mandatory).

## Alerting (recommended)

| Condition | Severity |
|-----------|----------|
| API `/health` down > 2 min | critical |
| Worker queue depth > threshold for 10 min | warning |
| Task failure rate > 10% over 15 min | warning |
| Redis / Postgres connection errors | critical |
| Daily AI spend > budget | warning |

Wire alerts in P6-12 when error monitoring is configured.

## Error Monitoring

**P6-12:** Integrate Sentry (or equivalent) for API and workers.

- Capture unhandled exceptions with `task_id` / `video_id` tags
- Do not send raw media or full transcripts to third-party monitoring
- Scrub API keys from breadcrumbs

## Tracing

Optional for V1. If added post-launch, propagate `request_id` from API into Celery task headers.

## Related

- [runbooks.md](./runbooks.md)
- [AGENTS.md](../../AGENTS.md#observability)
