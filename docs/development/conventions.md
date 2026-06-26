# Development Conventions

Pointers to detailed rules in [AGENTS.md](../../AGENTS.md#development-guidelines-for-ai-coding-agents).

## TypeScript (Extension & Web)

- Strict mode enabled
- Shared types only in `packages/shared-types`
- Platform code only in `apps/extension/platform-adapters/`
- No `any` unless required by extension APIs

## Python (API & Workers)

- Type hints on all functions
- Pydantic models for API and job payloads
- Deterministic, testable media helpers
- Log processing duration and model per AI step

## AI Output

- Never trust raw LLM output
- Parse → validate → normalize → save
- Store model name, prompt version, timestamp
- Keep `raw_analysis` for debug; expose cleaned data to UI

## Git / PR (for agents)

- One backlog task per focused change when possible
- Update BACKLOG status in same PR as implementation
- Do not commit secrets (`.env`, API keys)

## Local Development

```bash
pnpm install
python3 -m pip install -e .
docker compose -f infra/docker-compose.yml up -d
python3 -m alembic upgrade head
python3 -m uvicorn apps.api.main:app --reload --port 8000
python3 -m celery -A workers.celery_app worker --loglevel=info
pnpm --filter extension dev
```
