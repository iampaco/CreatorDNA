# CreatorDNA Documentation

> **For AI Agents:** Start at [STATUS.md](./STATUS.md), then follow links below.

## Quick Start (3 steps)

1. [STATUS.md](./STATUS.md) — next task ID and phase progress
2. [tasks/BACKLOG.md](./tasks/BACKLOG.md) — pick unblocked `todo`
3. [development/agent-playbook.md](./development/agent-playbook.md) — rules and module map

## V1 Scope

**Douyin Web** · Extension + Backend · 56 tasks · Launch when **P6-18** done  
Details: [product/vision-and-outcomes.md](./product/vision-and-outcomes.md) · [product/launch-criteria.md](./product/launch-criteria.md)

## Navigation

| Priority | Document | Purpose |
|----------|----------|---------|
| 0 | [STATUS.md](./STATUS.md) | Current progress and next action |
| 1 | [Agent Playbook](./development/agent-playbook.md) | How to work on this repo |
| 2 | [Task Backlog](./tasks/BACKLOG.md) | V1 checklist with dependencies |
| 3 | [Launch Criteria](./product/launch-criteria.md) | Production gates |
| 4 | [Architecture Overview](./architecture/overview.md) | System layers |
| 5 | [Module Ownership](./architecture/module-ownership.md) | Where code goes |
| 6 | [AGENTS.md](../AGENTS.md) | Constitution (schemas, APIs) |

## Document Layers

```txt
AGENTS.md              ← Stable constitution
docs/
├── STATUS.md          ← Living progress (update every task)
├── product/           ← Vision, V1 scope, launch gates
├── architecture/      ← Design, data flow, ADRs
├── development/       ← Playbook, getting started, testing, E2E
├── operations/        ← Deploy, security, observability, runbooks
├── api/               ← HTTP contracts and schemas
├── ai-pipeline/       ← Worker stages
├── compliance/        ← Safety rules
└── tasks/             ← BACKLOG, phases, PRODUCTION_GATES
```

## Reading Order by Task Type

### Starting a new feature

1. [STATUS.md](./STATUS.md) → [BACKLOG.md](./tasks/BACKLOG.md)
2. [module-ownership.md](./architecture/module-ownership.md)
3. [data-flow.md](./architecture/data-flow.md)
4. [AGENTS.md](../AGENTS.md) for schemas

### Browser extension

1. [decisions/001-mvp-platform-douyin.md](./architecture/decisions/001-mvp-platform-douyin.md)
2. [compliance/compliance.md](./compliance/compliance.md)
3. `.cursor/rules/extension.mdc`

### Backend / workers

1. [api/api.md](./api/api.md) · [api/schemas.md](./api/schemas.md)
2. [ai-pipeline/pipeline.md](./ai-pipeline/pipeline.md)
3. `.cursor/rules/api-workers.mdc`

### Production / launch

1. [launch-criteria.md](./product/launch-criteria.md)
2. [PRODUCTION_GATES.md](./tasks/PRODUCTION_GATES.md)
3. [operations/](./operations/)

## Project Status

| Area | Status |
|------|--------|
| V1 overall | 8 / 56 |
| Monorepo | Complete (P0-01) |
| Extension | Shell ready (P0-03) |
| Backend / Workers | Shell ready (P0-04, P0-05) |

Last updated: 2026-06-26
