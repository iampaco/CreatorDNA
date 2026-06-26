# Phase 0 — Foundation

**Goal:** Monorepo, shared types, local infra, and empty app shells.

**V1 tasks:** P0-01 through P0-08

## Acceptance Criteria (phase gate)

- [x] `pnpm install` succeeds at repo root
- [x] Extension dev server starts; MV3 build loads in Chrome
- [x] `GET /health` returns 200
- [x] Docker Compose: Postgres, Redis, MinIO healthy
- [x] All core DB tables migrated
- [x] Prompt placeholder files exist

## Task Checklist

### P0-01 — Monorepo init

- [x] `package.json` with workspace scripts
- [x] `pnpm-workspace.yaml` → `apps/*`, `packages/*`
- [x] Root `.gitignore` updated

**Acceptance:** `pnpm install` succeeds.

### P0-02 — shared-types

- [x] `CreatorProfile`, `CreatorVideoMeta`, `PlatformPageDetection`
- [x] `AnalysisTask`, `TaskStatus`, `TaskProgress`
- [x] `VideoStyleAnalysis`, `CreatorReport`

**Acceptance:** Package exports compile; matches [schemas.md](../../api/schemas.md).

### P0-03 — Extension shell

- [x] WXT under `apps/extension`
- [x] Entrypoints: content, background, popup, sidepanel, offscreen (stubs)
- [x] Manifest V3 + sidePanel permission + `*.douyin.com` host

**Acceptance:** Unpacked extension loads without errors.

### P0-04 — API shell

- [x] FastAPI `main.py`, `GET /health`
- [x] Config from env; CORS for extension origin

**Acceptance:** `curl localhost:8000/health` → 200.

### P0-05 — Workers layout

- [x] Celery app module; Redis broker config
- [x] Stub task registration

**Acceptance:** Worker process starts and connects to Redis.

### P0-06 — Infra

- [x] `infra/docker-compose.yml`: Postgres, Redis, MinIO
- [x] `.env.example` stub (completed in P6-06)

**Acceptance:** `docker compose up -d` → all services healthy.

### P0-07 — Migrations

- [x] Tables: creators, videos, transcripts, visual_analyses, video_style_analyses, creator_reports

**Acceptance:** Migrations apply cleanly on fresh DB.

### P0-08 — Prompts

- [x] video-structure-analysis.md, frame-visual-analysis.md, creator-report-generation.md, script-template-generation.md, safety-rewrite.md

**Acceptance:** Files exist under `packages/prompts/`.

## Next Phase

All P0 tasks `done` → start [Phase 1](./phase-1-single-video.md) at P1-01.
