# Runbooks

Operational procedures for common incidents. Expand with real commands when P6-10 deploys.

## API returns 503 / health check fails

**Symptoms:** Extension cannot upload; `/health` timeout.

**Check:**

1. API process running? Container logs?
2. Postgres connection — credentials, network, connection pool exhausted?
3. Redis reachable?

**Mitigate:** Restart API container. Scale connection pool if exhausted.

**Escalate:** If DB corrupt or migration failed, restore from backup (define backup policy in P6-10).

---

## Tasks stuck in `processing`

**Symptoms:** Progress frozen; `finishedVideos` not increasing.

**Check:**

1. Celery workers running? `celery inspect active`
2. Redis broker up?
3. Worker logs for `task_id` — ASR/LLM failure loop?
4. Dead-letter queue depth (P6-04)

**Mitigate:** Restart workers. Re-queue task if idempotent. Cancel task via API if user-facing cancel exists.

---

## ASR or LLM failures spike

**Symptoms:** Many tasks fail at `TRANSCRIBE_AUDIO` or `ANALYZE_VIDEO_STRUCTURE`.

**Check:**

1. Provider API status / rate limits
2. Invalid or expired API keys
3. Malformed audio (ffmpeg step logs)
4. LLM JSON parse failures — prompt or model change?

**Mitigate:** Rotate keys. Temporarily lower concurrency. Review `raw_analysis` in DB for parse errors.

---

## Storage full or upload failures

**Symptoms:** `POST /api/videos/upload` returns 5xx; MinIO/R2 errors in logs.

**Check:**

1. Bucket quota / disk space
2. Credentials and endpoint URL
3. CORS if browser direct upload

**Mitigate:** Free space; run TTL cleanup job (P6-05) manually if backlog.

---

## Extension capture denied

**Symptoms:** User sees permission error; not a server issue.

**Guide user:**

1. Re-click Analyze (user gesture required)
2. Grant tab capture permission in Chrome
3. Ensure active tab is Douyin video page, not chrome:// page

No server rollback needed.

---

## Rollback release

1. Pin API/worker image to previous version
2. If extension API contract changed, publish previous extension version to Chrome Web Store
3. Verify `/health` and one E2E path on staging before announcing

See [deployment.md](./deployment.md#rollback).

---

## Post-incident

- Log `task_id` and root cause in team channel
- Add test or alert if gap found
- Update this runbook with actual commands
