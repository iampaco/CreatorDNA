# Phase 6 Production Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan step-by-step. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete V1 production hardening (P6-01–P6-14, P6-17–P6-18); skip Chrome Web Store tasks P6-15/P6-16 per user request.

**Architecture:** Layer security (API key auth + Redis rate limits) on existing FastAPI routers; add structured logging middleware and Sentry; harden Celery with retries/DLQ/Beat TTL cleanup; containerize API/workers for staging; CI via GitHub Actions.

**Tech Stack:** FastAPI, Celery+Redis, boto3/MinIO, sentry-sdk, pytest, GitHub Actions, Docker

---

## Scope

| Include | Skip |
|---------|------|
| P6-01 auth | P6-15 store package |
| P6-02 rate limiting | P6-16 privacy copy |
| P6-03 structured logging | |
| P6-04 retry + DLQ | |
| P6-05 media TTL | |
| P6-06 env docs | |
| P6-07 CI | |
| P6-08 tests | |
| P6-09 staging | |
| P6-10 deploy/rollback | |
| P6-11 health/readiness | |
| P6-12 Sentry | |
| P6-13 AI quota/cost | |
| P6-14 staging E2E docs | |
| P6-17 security audit | |
| P6-18 launch review | |

## Implementation Order

```
Wave 1: P6-01 auth → P6-02 rate limit → P6-06 env
Wave 2: P6-03 logging → P6-11 health → P6-12 Sentry
Wave 3: P6-04 retry/DLQ → P6-05 TTL → P6-13 AI quota
Wave 4: P6-07 CI → P6-08 tests
Wave 5: P6-09 staging → P6-10 deploy docs → P6-14 E2E → P6-17 security → P6-18 launch
```

## Key Files

| Area | Create | Modify |
|------|--------|--------|
| Auth | `apps/api/deps/auth.py` | `config.py`, routers, `api-client.ts`, sidepanel |
| Rate limit | `apps/api/middleware/rate_limit.py` | `main.py`, `config.py` |
| Logging | `apps/api/middleware/request_context.py`, `workers/logging_config.py` | `main.py`, `celery_app.py` |
| TTL | `workers/tasks/media_cleanup.py` | `storage.py`, `celery_app.py` |
| Infra | `infra/Dockerfile.api`, `infra/Dockerfile.worker`, `infra/docker-compose.staging.yml` | `docker-compose.yml` |
| CI | `.github/workflows/ci.yml` | `package.json`, `pyproject.toml` |
| Tests | `tests/conftest.py`, `tests/test_auth.py`, etc. | existing tests |

---

## Wave 1: Security Foundation

### Task 1: API Key Auth (P6-01)

- Add `api_secret_key`, `environment` to Settings
- `verify_api_key` dependency: require `Authorization: Bearer <key>` when key configured or env != local
- Protect POST upload, creator-analysis, export create
- Extension: `getAuthHeaders()` in api-client; sidepanel settings for API key
- Tests: 401 without key, 200 with key

### Task 2: Rate Limiting (P6-02)

- Redis sliding window per client IP + API key
- Apply to upload and creator-analysis POST routes
- Return 429 with `rate_limited` error code

### Task 3: Environment Documentation (P6-06)

- Complete `.env.example`
- Add `docs/operations/secrets.md`

---

## Wave 2: Observability

### Task 4: Structured Logging (P6-03)

- Request ID middleware (`X-Request-ID`)
- JSON log formatter for API and workers
- Log task_id, video_id, step, duration_ms in worker tasks

### Task 5: Health + Readiness (P6-11)

- `GET /health` — liveness (always ok if process up)
- `GET /ready` — checks Postgres, Redis, Celery worker ping
- Return 503 when dependencies down

### Task 6: Sentry (P6-12)

- `sentry-sdk[fastapi,celery]` in pyproject
- Init when `SENTRY_DSN` set
- Scrub Authorization headers
- Staging-only `POST /debug/sentry-test` route

---

## Wave 3: Reliability

### Task 7: Celery Retry + DLQ (P6-04)

- `task_autoretry_for`, `max_retries=3`, exponential backoff
- Dead letter queue route for max-retries-exceeded
- Idempotency via existing `_clear_prior_results`

### Task 8: Media TTL Cleanup (P6-05)

- `StorageService.delete_object`, `list_objects_with_prefix`
- Beat task deletes capture.webm older than `MEDIA_TTL_HOURS`
- Keep frames/exports per retention policy

### Task 9: AI Quota + Cost (P6-13)

- `workers/services/quota.py` — Redis daily counter per deployment
- Log tokens/cost estimate in llm/asr/vision services
- Fail with `quota_exceeded` when over limit

---

## Wave 4: Quality

### Task 10: GitHub Actions CI (P6-07)

- Lint: pnpm typecheck, ruff check
- Test: pytest
- Build: extension build
- pip audit / npm audit (continue-on-error for audit)

### Task 11: Core Tests (P6-08)

- Auth, rate limit, health, media cleanup, task status, JSON validation
- Shared conftest with auth headers and env overrides

---

## Wave 5: Deploy & Launch

### Task 12: Staging (P6-09)

- Dockerfiles for API and worker (+ beat)
- `docker-compose.staging.yml` full stack
- Document staging deploy in deployment.md

### Task 13: Production Deploy (P6-10)

- Rollback procedure with image tags
- Migration commands
- Runbook real commands

### Task 14: Launch (P6-14, P6-17, P6-18)

- e2e-checklist Test D staging procedure
- security.md checklist checked
- launch-criteria.md boxes checked
- BACKLOG + STATUS → V1 complete (16/16 Phase 6 tasks done, excluding P6-15/16)
