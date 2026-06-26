# Getting Started

Local development setup. **Concrete commands are filled in when Phase 0 (P0-01–P0-06) completes.**

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Extension, monorepo |
| pnpm | 9+ | Package manager |
| Python | 3.11+ | API, workers |
| Docker | latest | Postgres, Redis, MinIO |
| ffmpeg | 6+ | Worker media processing (host or container) |

## Quick Start (after Phase 0)

```bash
# 1. Clone and install
git clone <repo-url> creator-dna && cd creator-dna
pnpm install

# 2. Environment
cp .env.example .env
# Edit: DATABASE_URL, REDIS_URL, STORAGE_*, OPENAI_API_KEY, API_SECRET_KEY

# 3. Infrastructure
docker compose -f infra/docker-compose.yml up -d

# 4. Database migrations
# (command TBD — Alembic or similar at P0-07)

# 5. API
cd apps/api && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 6. Workers (separate terminal)
celery -A workers.celery_app worker --loglevel=info

# 7. Extension (separate terminal)
pnpm --filter extension dev
# Load unpacked extension from apps/extension/.output/chrome-mv3
```

## Extension Dev

1. Run `pnpm --filter extension dev`
2. Open `chrome://extensions` → Developer mode → Load unpacked
3. Point to WXT output directory (documented in extension README at P0-03)
4. Open Douyin video page → open side panel

## API Base URL

Extension dev build should target `http://localhost:8000`. Configure via `VITE_API_URL` or equivalent at P0-03.

## Verify Stack

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"} (after P0-04)
```

## Common Issues

| Issue | Fix |
|-------|-----|
| Extension not detecting Douyin | Check host permissions in manifest |
| Upload 401 | Set API key in extension storage / env |
| Worker not processing | Redis up? Celery worker running? |
| ffmpeg not found | Install on host or use worker Docker image with ffmpeg |

## Related

- [deployment.md](../operations/deployment.md)
- [agent-playbook.md](./agent-playbook.md)
- [e2e-checklist.md](./e2e-checklist.md)
