# Monorepo Structure

Target layout (not yet scaffolded):

```txt
creator-dna/
├── apps/
│   ├── extension/          # WXT browser extension
│   │   ├── entrypoints/
│   │   │   ├── content.ts
│   │   │   ├── background.ts
│   │   │   ├── popup/
│   │   │   ├── sidepanel/
│   │   │   └── offscreen/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── platform-adapters/
│   │   └── wxt.config.ts
│   ├── web/                  # Next.js dashboard (post-MVP)
│   └── api/                  # FastAPI gateway
│       ├── main.py
│       ├── routers/
│       ├── services/
│       ├── schemas/
│       └── config/
├── workers/
│   ├── video_preprocess_worker.py
│   ├── asr_worker.py
│   ├── vision_worker.py
│   ├── style_analysis_worker.py
│   └── report_worker.py
├── packages/
│   ├── shared-types/
│   ├── prompts/
│   ├── ai-clients/
│   ├── platform-core/
│   └── utils/
├── infra/
│   ├── docker-compose.yml
│   ├── postgres/
│   ├── redis/
│   └── storage/
├── docs/                     # This documentation system
├── AGENTS.md
├── package.json
└── pnpm-workspace.yaml
```

## Package Manager

- **pnpm** workspaces for TypeScript apps and packages
- Python apps/workers: separate `requirements.txt` or `pyproject.toml` per app (TBD at scaffold time)

## Import Rules

- `apps/extension` may import from `packages/*`, not from `apps/api` or `workers`
- `apps/api` may import from `packages/*` (shared types via code gen or duplicate Pydantic models — pick one at scaffold)
- `workers` read/write DB and storage; call `packages/ai-clients` if shared
- `platform-adapters` implement interface from `packages/platform-core`

## First Scaffold Task

See [Phase 0](../tasks/phases/phase-0-foundation.md) in the task backlog.
