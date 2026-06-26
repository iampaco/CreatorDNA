# Runbooks

Operational procedures for common incidents.

## API returns 503 / health check fails

**Symptoms:** Extension cannot upload; `/health` or `/ready` timeout.

**Check:**

```bash
curl -v http://localhost:8000/health
curl -v http://localhost:8000/ready
docker compose -f infra/docker-compose.staging.yml logs api --tail=100
docker compose -f infra/docker-compose.staging.yml ps
```

1. API process running? Container logs?
2. Postgres connection — credentials, network, connection pool exhausted?
3. Redis reachable?

**Mitigate:** Restart API container:

```bash
docker compose -f infra/docker-compose.staging.yml restart api
```

**Escalate:** If DB corrupt or migration failed, restore from backup.

---

## Tasks stuck in `processing`

**Symptoms:** Progress frozen; `finishedVideos` not increasing.

**Check:**

```bash
celery -A workers.celery_app inspect active
celery -A workers.celery_app inspect reserved
docker compose -f infra/docker-compose.staging.yml logs worker --tail=200
redis-cli -u $REDIS_URL LLEN dead_letter
```

1. Celery workers running?
2. Redis broker up?
3. Worker logs for `task_id` — ASR/LLM failure loop?
4. Dead-letter queue depth

**Mitigate:**

```bash
docker compose -f infra/docker-compose.staging.yml restart worker
```

Re-queue task if idempotent (upload creates new task automatically on retry).

---

## ASR or LLM failures spike

**Symptoms:** Many tasks fail at `TRANSCRIBE_AUDIO` or `ANALYZE_VIDEO_STRUCTURE`.

**Check:**

1. Provider API status / rate limits
2. Invalid or expired `OPENAI_API_KEY`
3. Malformed audio (ffmpeg step logs)
4. LLM JSON parse failures — prompt or model change?
5. Daily quota: `redis-cli GET ai_quota:$(date -u +%Y-%m-%d):TRANSCRIBE_AUDIO`

**Mitigate:** Rotate keys. Temporarily lower worker concurrency. Increase `AI_DAILY_QUOTA` if legitimate traffic.

---

## Storage full or upload failures

**Symptoms:** `POST /api/videos/upload` returns 5xx; MinIO/R2 errors in logs.

**Check:**

1. Bucket quota / disk space
2. Credentials and endpoint URL
3. CORS if browser direct upload

**Mitigate:**

```bash
# Manual TTL cleanup trigger
celery -A workers.celery_app call workers.tasks.media_cleanup.cleanup_expired_media
```

---

## Rate limit / 429 errors

**Symptoms:** Extension shows "请求过于频繁".

**Check:** `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` settings.

**Mitigate:** Increase limits for staging; verify client is not retry-looping.

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

1. Pin API/worker image to previous version (see [deployment.md](./deployment.md#rollback))
2. If extension API contract changed, publish previous extension version
3. Verify `/ready` and one E2E path on staging before announcing

---

## Post-incident

- Log `task_id` and root cause in team channel
- Add test or alert if gap found
- Update this runbook with actual commands
