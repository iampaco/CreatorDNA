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

## API Base URL & Auth

- Local default: `http://localhost:8000` (no auth when `ENVIRONMENT=local` and `API_SECRET_KEY` unset)
- Staging/production: set `API_SECRET_KEY` in `.env`; enter the same key in the extension side panel **连接设置**
- Text LLM: set `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_CHAT_MODEL` for DeepSeek-compatible report generation
- ASR/vision: set `OPENAI_API_KEY` for real transcription and OpenAI vision; leave unset only for dev mock mode
- Full variable reference: [.env.example](../../.env.example), [secrets.md](../operations/secrets.md)

## Staging Full Stack

```bash
docker compose -f infra/docker-compose.staging.yml up -d --build
docker compose -f infra/docker-compose.staging.yml exec api alembic upgrade head
curl http://localhost:8000/ready
```

## Verify Stack

```bash
pnpm typecheck
pnpm lint
pnpm test
pnpm --filter extension build
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Common Issues

| Issue | Fix |
|-------|-----|
| Extension not detecting Douyin | Check `host_permissions` for `*.douyin.com` in manifest |
| Upload 401 | Set API key in side panel **连接设置** or disable auth locally |
| Worker not processing | Redis up? `docker compose ... ps` shows redis healthy |
| Alembic connection refused | Start Postgres: `docker compose -f infra/docker-compose.yml up -d` |
| ffmpeg not found | Install on host or use worker Docker image with ffmpeg |

## Related

- [deployment.md](../operations/deployment.md)
- [agent-playbook.md](./agent-playbook.md)
- [e2e-checklist.md](./e2e-checklist.md)
