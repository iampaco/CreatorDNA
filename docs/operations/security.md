# Security

Security requirements for V1 production launch. Verified in **P6-17**.

## Authentication

| Surface | Requirement |
|---------|-------------|
| Extension → API | API key or short-lived JWT in `Authorization` header |
| API → public | No unauthenticated upload or task creation |
| Admin / internal | Separate credentials; not embedded in extension |

Extension API keys: per-user or per-deployment key distributed via secure onboarding (not hard-coded in public repo).

## Transport

- HTTPS only in staging and production
- TLS for Postgres and Redis where provider supports it
- No mixed-content extension calls to HTTP API in prod

## Secrets Management

- All secrets in environment variables or secret manager
- `.env` gitignored; `.env.example` has placeholders only
- Rotate keys on compromise or team member offboarding
- Never log API keys, tokens, or raw Authorization headers

## Input Validation

- Pydantic schemas on all API bodies
- File upload: max size, allowed MIME types (webm, audio)
- Sanitize `videoUrl` — must match Douyin URL patterns
- Rate limit per IP / per API key (P6-02)

## Data Retention

| Data | Retention |
|------|-----------|
| Raw captured media | Delete after analysis TTL (default: 24–72h, configurable) |
| Transcripts & analyses | Retain per product policy; user may request deletion (future) |
| Logs | 30–90 days; no full transcript bodies in logs |

TTL job: **P6-05**.

## AI & Privacy

- Audio sent to OpenAI STT per [ADR 003](../architecture/decisions/003-asr-provider.md) — disclose in privacy policy
- Do not send PII unnecessarily in LLM prompts
- `raw_analysis` in DB is debug-only; not exposed to other users

## Extension Permissions (Chrome)

Document justification for each manifest permission in **P6-16**:

| Permission | Justification |
|------------|---------------|
| `sidePanel` | Display analysis reports |
| `tabCapture` | User-initiated video/audio capture on active tab |
| `storage` | Local task state |
| Host permission `*.douyin.com` | Detect page and extract visible metadata |

## Security Checklist (P6-17)

- [x] Unauthenticated API calls return 401/403
- [x] Upload size limits enforced (`UPLOAD_MAX_BYTES`, content type validation)
- [x] SQL injection prevented (ORM / parameterized queries)
- [x] CORS restricted to extension origin(s)
- [x] Dependencies scanned in CI (npm audit, pip audit)
- [x] No secrets in git history (scan before launch)
- [x] Media TTL cleanup verified (Celery Beat + `cleanup_expired_media`)
- [x] Error responses do not leak stack traces to clients in production

## Related

- [compliance.md](../compliance/compliance.md)
- [launch-criteria.md](../product/launch-criteria.md)
