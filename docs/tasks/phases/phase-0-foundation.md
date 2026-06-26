# Phase 0 — Foundation

**Goal:** Monorepo, shared types, local infra, and empty app shells.

**V1 tasks:** P0-01 through P0-08

## Acceptance Criteria (phase gate)

- [ ] `pnpm install` succeeds at repo root
- [ ] Extension dev server starts; MV3 build loads in Chrome
- [ ] `GET /health` returns 200
- [ ] Docker Compose: Postgres, Redis, MinIO healthy
- [ ] All core DB tables migrated
- [ ] Prompt placeholder files exist

## Task Checklist

### P0-01 — Monorepo init

- [ ] `package.json` with workspace scripts
- [ ] `pnpm-workspace.yaml` → `apps/*`, `packages/*`
- [ ] Root `.gitignore` updated

**Acceptance:** `pnpm install` succeeds.

### P0-02 — shared-types

- [ ] `CreatorProfile`, `CreatorVideoMeta`, `PlatformPageDetection`
- [ ] `AnalysisTask`, `TaskStatus`, `TaskProgress`
- [ ] `VideoStyleAnalysis`, `CreatorReport`

**Acceptance:** Package exports compile; matches [schemas.md](../../api/schemas.md).

### P0-03 — Extension shell

- [ ] WXT under `apps/extension`
- [ ] Entrypoints: content, background, popup, sidepanel, offscreen (stubs)
- [ ] Manifest V3 + sidePanel permission + `*.douyin.com` host

**Acceptance:** Unpacked extension loads without errors.

### P0-04 — API shell

- [ ] FastAPI `main.py`, `GET /health`
- [ ] Config from env; CORS for extension origin

**Acceptance:** `curl localhost:8000/health` → 200.

### P0-05 — Workers layout

- [ ] Celery app module; Redis broker config
- [ ] Stub task registration

**Acceptance:** Worker process starts and connects to Redis.

### P0-06 — Infra

- [ ] `infra/docker-compose.yml`: Postgres, Redis, MinIO
- [ ] `.env.example` stub (completed in P6-06)

**Acceptance:** `docker compose up -d` → all services healthy.

### P0-07 — Migrations

- [ ] Tables: creators, videos, transcripts, visual_analyses, video_style_analyses, creator_reports

**Acceptance:** Migrations apply cleanly on fresh DB.

### P0-08 — Prompts

- [ ] video-structure-analysis.md, frame-visual-analysis.md, creator-report-generation.md, script-template-generation.md, safety-rewrite.md

**Acceptance:** Files exist under `packages/prompts/`.

## Next Phase

All P0 tasks `done` → start [Phase 1](./phase-1-single-video.md) at P1-01.
