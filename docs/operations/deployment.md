# Deployment

## Environments

| Environment | Purpose | Storage | Notes |
|-------------|---------|---------|-------|
| `local` | Developer machines | MinIO via docker-compose | Full stack optional |
| `staging` | Pre-prod E2E | R2 or S3 staging bucket | Mirrors prod topology |
| `production` | Live users | R2 or S3 prod bucket | Chrome extension points here |

## Topology (V1)

```txt
                    ┌─────────────────┐
                    │ Chrome Extension │
                    └────────┬────────┘
                             │ HTTPS + API key
                    ┌────────▼────────┐
                    │  FastAPI (API)   │
                    │  /health         │
                    └────────┬────────┘
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌───────▼──────┐ ┌─────▼─────┐
     │ PostgreSQL │  │    Redis     │ │ R2 / S3   │
     └────────────┘  └───────┬──────┘ └───────────┘
                             │
                    ┌────────▼────────┐
                    │ Celery Workers   │
                    │ (N replicas)     │
                    └─────────────────┘
```

## Local Development

> Commands finalized in Phase 0 (P0-06). Placeholder flow:

```bash
# Infra
docker compose -f infra/docker-compose.yml up -d

# API (from repo root)
cd apps/api && uvicorn main:app --reload --port 8000

# Workers
celery -A workers.celery_app worker --loglevel=info

# Extension
pnpm --filter extension dev
```

## Staging / Production

Implemented in **P6-09** and **P6-10**. Target options:

| Option | Fit for V1 |
|--------|------------|
| Single VPS + docker-compose | Simplest; good for early launch |
| Fly.io / Railway / Render | Managed containers + Postgres add-on |
| AWS ECS / GCP Cloud Run | Scale later |

### Required services

- FastAPI container (horizontally scalable behind load balancer)
- Celery worker container(s) — separate from API
- Managed PostgreSQL
- Managed Redis
- Object storage (R2 or S3 per [ADR 004](../architecture/decisions/004-object-storage.md))

### Deploy checklist

- [ ] Environment variables set (no secrets in image)
- [ ] Database migrations applied
- [ ] Redis reachable from API and workers
- [ ] Storage bucket CORS allows extension origin if direct upload
- [ ] `EXTENSION_API_URL` baked into extension build per environment
- [ ] Health checks wired to orchestrator

## Rollback

1. Revert API/worker image to previous tag
2. Run DB migration down only if backward-compatible (prefer forward-only migrations)
3. Extension: publish previous Chrome Web Store version if API contract broke

Document actual rollback commands in this file when P6-10 completes.

## Related

- [getting-started.md](../development/getting-started.md)
- [security.md](./security.md)
- [ADR 004](../architecture/decisions/004-object-storage.md)
