# Agent Playbook

> **Audience:** AI coding agents and human developers.
> **Goal:** Reduce wrong assumptions, scope creep, and compliance violations.

## Before You Code

1. Read [STATUS.md](../STATUS.md) — confirm next task ID.
2. Read [Vision & Outcomes](../product/vision-and-outcomes.md) — confirm task aligns with V1 scope.
3. Open [BACKLOG.md](../tasks/BACKLOG.md) — work only on listed, unblocked tasks unless the user explicitly requests otherwise.
4. Skim [Module Ownership](../architecture/module-ownership.md) — place code in the correct path.
5. Check [Compliance](../compliance/compliance.md) — especially for extension capture.

## Core Principles (Non-Negotiable)

- **User-triggered capture only.** No silent recording or hidden tab capture.
- **Structure over copying.** Analyze patterns; do not clone scripts or identity.
- **Browser-assisted, not crawler.** Collect what the user already sees in their session.
- **Typed boundaries.** Shared types in `packages/shared-types`; validate all LLM JSON.
- **One platform in V1.** Douyin Web only ([ADR 001](../architecture/decisions/001-mvp-platform-douyin.md)).

## Where to Put Code

| Change type | Location |
|-------------|----------|
| DOM / page detection | `apps/extension/platform-adapters/douyin-web.adapter.ts` |
| Extension UI | `apps/extension/entrypoints/popup/`, `sidepanel/` |
| Service worker orchestration | `apps/extension/entrypoints/background.ts` |
| Media recording | `apps/extension/entrypoints/offscreen/` |
| HTTP routes | `apps/api/routers/` |
| Business logic | `apps/api/services/` |
| Background jobs | `workers/` |
| LLM prompts | `packages/prompts/` |
| Cross-app types | `packages/shared-types/` |

Never put platform-specific selectors in shared packages.

## Task ID & Status

- IDs: `P{phase}-{seq}` (e.g. P1-02, P6-18)
- Status: `todo` | `in_progress` | `blocked` | `done` | `deferred` only

## Task Completion Checklist

When finishing a backlog item:

- [ ] Code lives in the correct module (see [module-ownership.md](../architecture/module-ownership.md))
- [ ] Types added or updated in `packages/shared-types` if contracts changed
- [ ] Error cases from [AGENTS.md](../../AGENTS.md#error-handling) considered
- [ ] No compliance violations (see [compliance.md](../compliance/compliance.md))
- [ ] [BACKLOG.md](../tasks/BACKLOG.md) + [STATUS.md](../STATUS.md) updated
- [ ] Phase file checkboxes updated in `docs/tasks/phases/`
- [ ] If API or schema changed: [api/schemas.md](../api/schemas.md), [api.md](../api/api.md)
- [ ] Tests per [testing-strategy.md](./testing-strategy.md) when applicable

## Extension-Specific Rules

- Use **WXT** + **React** + **TypeScript** + **Manifest V3**.
- Content script: layered extraction (URL → anchors → semantic DOM → platform selectors → manual fallback).
- Background worker: no heavy AI or ffmpeg logic.
- Offscreen document: only for user-initiated `MediaRecorder` / tab capture flows.
- Side panel: primary report UI for MVP.

## Backend / Worker Rules

- **FastAPI** + **Pydantic** for API; type hints everywhere in Python.
- Jobs must be **idempotent** where possible.
- Log: `task_id`, `video_id`, step, model, duration, errors, retry count.
- Wrap `ffmpeg` and external APIs with explicit error handling.
- Store model name, prompt version, and timestamp with each AI output.

## What Not to Do

- Do not build multi-platform adapters before single-video E2E works.
- Do not send raw transcripts of dozens of videos to an LLM for aggregation.
- Do not store full videos longer than needed for analysis.
- Do not bypass login, DRM, or paywalls.
- Do not start Phase 5 (multi-platform, teams) unless user explicitly requests.
- Do not add web dashboard (P4-04/P4-05 deferred) in V1.

## Escalation

If a task requires a product decision not covered in docs:

1. Note the ambiguity in BACKLOG under the task.
2. Propose the smallest compliant default.
3. Ask the user only when the choice materially affects architecture or compliance.
