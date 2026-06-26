# Deployment

## Environments

| Environment | Purpose | Storage | Notes |
|-------------|---------|---------|-------|
| `local` | Developer machines | MinIO via docker-compose | Auth optional |
| `staging` | Pre-prod E2E | MinIO or R2/S3 staging bucket | Full stack via staging compose |
| `production` | Live users | R2 or S3 prod bucket | Chrome extension points here |

## Topology (V1)

```txt
                    ┌─────────────────┐
                    │ Chrome Extension │
                    └────────┬────────┘
                             │ HTTPS + Bearer API key
                    ┌────────▼────────┐
                    │  FastAPI (API)   │
                    │  /health /ready  │
                    └────────┬────────┘
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌───────▼──────┐ ┌─────▼─────┐
     │ PostgreSQL │  │    Redis     │ │ R2 / S3   │
     └────────────┘  └───────┬──────┘ └───────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌───────▼──────┐
     │ Celery     │  │ Celery Beat  │
     │ Workers    │  │ (TTL cleanup)│
     └────────────┘  └──────────────┘
```

## Local Development

```bash
# Infra only
docker compose -f infra/docker-compose.yml up -d

# API (from repo root)
uvicorn apps.api.main:app --reload --port 8000

# Workers
celery -A workers.celery_app worker --loglevel=info -Q analysis,exports,maintenance,dead_letter

# Beat (TTL cleanup)
celery -A workers.celery_app beat --loglevel=info

# Extension
pnpm --filter extension dev
```

## Staging (Full Stack)

```bash
# 1. Copy and configure secrets
cp .env.example .env
# Set API_SECRET_KEY, OPENAI_API_KEY (optional for mock mode)

# 2. Start full stack
docker compose -f infra/docker-compose.staging.yml up -d --build

# 3. Run migrations
docker compose -f infra/docker-compose.staging.yml exec api alembic upgrade head

# 4. Verify readiness
curl http://localhost:8000/health
curl http://localhost:8000/ready

# 5. Load extension (dev build) with API key in side panel settings
pnpm --filter extension build
# Load apps/extension/.output/chrome-mv3 in chrome://extensions
```

### Staging E2E (P6-14)

Follow [e2e-checklist.md](../development/e2e-checklist.md) **Test D** against `http://localhost:8000` with API key configured.

## Production Deploy

### Pre-deploy checklist

- [ ] Environment variables set in secret manager (see [secrets.md](./secrets.md))
- [ ] `ENVIRONMENT=production`
- [ ] `API_SECRET_KEY` configured; extension distributed with same key
- [ ] Database migrations applied: `alembic upgrade head`
- [ ] Redis reachable from API and workers
- [ ] Storage bucket configured (R2/S3)
- [ ] `SENTRY_DSN` configured
- [ ] Health checks wired: `/health` (liveness), `/ready` (readiness)

### Deploy procedure

```bash
# Build and tag images
export IMAGE_TAG=$(git rev-parse --short HEAD)
docker build -f infra/Dockerfile.api -t creatordna-api:$IMAGE_TAG .
docker build -f infra/Dockerfile.worker -t creatordna-worker:$IMAGE_TAG .
docker build -f infra/Dockerfile.beat -t creatordna-beat:$IMAGE_TAG .

# Push to registry (example)
docker tag creatordna-api:$IMAGE_TAG registry.example.com/creatordna-api:$IMAGE_TAG
docker push registry.example.com/creatordna-api:$IMAGE_TAG
# Repeat for worker and beat

# Deploy (platform-specific)
# - Update container image tag to $IMAGE_TAG
# - Run migrations as one-off job
# - Rolling restart: API → workers → beat

# Post-deploy verification
curl -f https://api.example.com/health
curl -f https://api.example.com/ready
```

### Rollback

1. **API/Workers:** Revert container image tag to previous known-good `$PREV_TAG`
2. **Database:** Prefer forward-only migrations. Only run `alembic downgrade` if the migration is explicitly reversible and tested
3. **Extension:** If API contract changed, users need previous extension build (Chrome Web Store rollback is manual)
4. **Verify:** Run `/ready` and one upload/analysis smoke test on staging before announcing rollback complete

```bash
# Example rollback (docker-compose staging)
export PREV_TAG=abc1234
docker compose -f infra/docker-compose.staging.yml pull
IMAGE_TAG=$PREV_TAG docker compose -f infra/docker-compose.staging.yml up -d api worker beat
curl -f http://localhost:8000/ready
```

## Related

- [getting-started.md](../development/getting-started.md)
- [secrets.md](./secrets.md)
- [security.md](./security.md)
- [runbooks.md](./runbooks.md)
- [ADR 004](../architecture/decisions/004-object-storage.md)
