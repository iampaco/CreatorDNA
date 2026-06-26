# Getting Started

Local development setup for CreatorDNA (Phase 0 complete).

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Extension, monorepo |
| pnpm | 9+ | Package manager |
| Python | 3.11+ | API, workers |
| Docker | latest | Postgres, Redis, MinIO |
| ffmpeg | 6+ | Worker media processing (Phase 1+) |

Optional: [uv](https://docs.astral.sh/uv/) for faster Python installs (`uv sync`). Fallback: `python3 -m pip install -e .`

## Quick Start

```bash
# 1. Clone and install JS workspace
git clone <repo-url> creator-dna && cd creator-dna
pnpm install

# 2. Python dependencies (from repo root)
python3 -m pip install -e .
# or: uv sync

# 3. Environment
cp .env.example .env

# 4. Infrastructure
docker compose -f infra/docker-compose.yml up -d

# 5. Database migrations
python3 -m alembic upgrade head

# 6. API (separate terminal)
python3 -m uvicorn apps.api.main:app --reload --port 8000

# 7. Workers (separate terminal; requires Redis)
python3 -m celery -A workers.celery_app worker --loglevel=info

# 8. Extension (separate terminal)
pnpm --filter extension dev
# Production build: pnpm --filter extension build
# Load unpacked: apps/extension/.output/chrome-mv3
```

## Extension Dev

1. Run `pnpm --filter extension dev` (or `build` for production bundle)
2. Open `chrome://extensions` → Developer mode → Load unpacked
3. Select `apps/extension/.output/chrome-mv3`
4. Open a Douyin page → open side panel from extension icon

## API Base URL

Extension will target `http://localhost:8000` in Phase 1 (`VITE_API_URL` or equivalent).

## Verify Stack

```bash
pnpm typecheck
pnpm --filter extension build
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# After docker + migrations:
docker compose -f infra/docker-compose.yml ps
python3 -m alembic current
```

## Common Issues

| Issue | Fix |
|-------|-----|
| Extension not detecting Douyin | Check `host_permissions` for `*.douyin.com` in manifest |
| Upload 401 | Set API key in extension storage / env (P6-01) |
| Worker not processing | Redis up? `docker compose ... ps` shows redis healthy |
| Alembic connection refused | Start Postgres: `docker compose -f infra/docker-compose.yml up -d` |
| ffmpeg not found | Install on host or use worker Docker image with ffmpeg |

## Related

- [deployment.md](../operations/deployment.md)
- [agent-playbook.md](./agent-playbook.md)
- [e2e-checklist.md](./e2e-checklist.md)
