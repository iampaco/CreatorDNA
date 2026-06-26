# Module Ownership

Where code belongs and which docs to update when changing it.

## Ownership Map

| Module | Path | Owns | Docs to update on change |
|--------|------|------|--------------------------|
| Extension content | `apps/extension/entrypoints/content.ts` | Adapter injection, DOM events | data-flow, phase-1 |
| Extension background | `apps/extension/entrypoints/background.ts` | Task state, API calls, capture orchestration | data-flow, agent-playbook |
| Extension offscreen | `apps/extension/entrypoints/offscreen/` | MediaRecorder, upload chunks | compliance, data-flow |
| Extension side panel | `apps/extension/entrypoints/sidepanel/` | Report UI, Analyze trigger | vision-and-outcomes |
| Extension popup | `apps/extension/entrypoints/popup/` | Settings, API key entry (if any) | security |
| Platform adapters | `apps/extension/platform-adapters/` | Douyin-specific extraction | ADR 001, phase-1/2 |
| Platform core | `packages/platform-core/` | `PlatformAdapter` interface | api/schemas (types) |
| Shared types | `packages/shared-types/` | TS contracts | api/schemas.md |
| Prompts | `packages/prompts/` | LLM prompt files | ai-pipeline/pipeline |
| AI clients | `packages/ai-clients/` | Provider wrappers | ADR 003, observability |
| API gateway | `apps/api/` | HTTP routes, validation, enqueue | api/api.md, api/schemas.md |
| API routers | `apps/api/routers/` | Per-resource endpoints | api/api.md |
| API services | `apps/api/services/` | Business logic | architecture/overview |
| API schemas | `apps/api/schemas/` | Pydantic models | api/schemas.md |
| Workers | `workers/` | Celery tasks, ffmpeg, AI steps | ai-pipeline, observability |
| Infra | `infra/` | docker-compose, DB init | deployment, getting-started |
| Web dashboard | `apps/web/` | **Deferred post-V1** | — |

## Boundary Rules

```txt
extension ──HTTP──► api ──enqueue──► workers
     │                  │                  │
     └── adapters       └── postgres       └── storage (R2/MinIO)
                        └── redis
```

- **No** ffmpeg or LLM calls in extension
- **No** Douyin CSS selectors in `packages/` (adapters only)
- **No** browser APIs in workers
- Shared types are source of truth for cross-boundary contracts

## Agent Routing

| If task mentions… | Start in… |
|-------------------|-----------|
| DOM, scroll, video list | `platform-adapters/douyin-web.adapter.ts` |
| Recording, capture | `offscreen/` + `background.ts` |
| Report UI | `sidepanel/` |
| Upload, tasks, reports API | `apps/api/routers/` |
| ASR, frames, LLM | `workers/` |
| Prompt wording | `packages/prompts/` |
| Auth, rate limit, deploy | `apps/api/` + `docs/operations/` |

## Related

- [agent-playbook.md](../development/agent-playbook.md)
- [monorepo-structure.md](./monorepo-structure.md)
