# Task Backlog

> **Agents:** Pick unblocked `todo` items from the lowest incomplete V1 phase. Update [STATUS.md](../STATUS.md) when status changes.

## V1 Scope

**Platform:** Douyin Web | **Product:** Chrome Extension + Backend  
**V1 complete when:** P6-18 Launch Review is `done` ([launch-criteria.md](../product/launch-criteria.md))

Post-launch work: [Phase 5](#phase-5--post-launch) (not counted in V1 progress).

## Summary

| Phase | Name | V1 | Progress |
|-------|------|----|----------|
| 0 | [Foundation](./phases/phase-0-foundation.md) | Yes | 8 / 8 |
| 1 | [Single Video](./phases/phase-1-single-video.md) | Yes | 12 / 12 |
| 2 | [Creator Batch](./phases/phase-2-creator-batch.md) | Yes | 8 / 8 |
| 3 | [Visual Analysis](./phases/phase-3-visual.md) | Yes | 0 / 6 |
| 4 | [Export](./phases/phase-4-export.md) | Yes | 0 / 4 |
| 6 | [Production](./phases/phase-6-production.md) | Yes | 0 / 18 |
| 5 | [Platform (post-launch)](./phases/phase-5-platform.md) | No | 0 / 7 |

**V1 total: 28 / 56**

---

## Phase 0 — Foundation

| ID | Task | Acceptance | Status | Depends on |
|----|------|------------|--------|------------|
| P0-01 | Initialize pnpm monorepo | `pnpm install` succeeds at root | `done` | — |
| P0-02 | Scaffold `packages/shared-types` | Core interfaces export without error | `done` | P0-01 |
| P0-03 | Scaffold `apps/extension` (WXT+React+TS) | Dev build produces loadable MV3 extension | `done` | P0-01, P0-02 |
| P0-04 | Scaffold `apps/api` (FastAPI) | `GET /health` returns 200 | `done` | P0-01 |
| P0-05 | Scaffold `workers/` layout | Celery app imports and connects to Redis | `done` | P0-04 |
| P0-06 | `infra/docker-compose.yml` | Postgres, Redis, MinIO start healthy | `done` | P0-04 |
| P0-07 | Database migrations | All AGENTS.md tables exist | `done` | P0-06 |
| P0-08 | `packages/prompts/` placeholders | Five prompt files present | `done` | P0-01 |

---

## Phase 1 — Single Video MVP (Douyin Web)

| ID | Task | Acceptance | Status | Depends on |
|----|------|------------|--------|------------|
| P1-01 | `PlatformAdapter` in platform-core | Interface compiles; four methods defined | `done` | P0-02 |
| P1-02 | `douyin-web.adapter.ts` | Detects video/creator URLs; extracts current video meta | `done` | P1-01, P0-03 |
| P1-03 | Content script | Sends page detection + video meta to background | `done` | P1-02 |
| P1-04 | Background state machine | idle→capturing→uploading→processing→done/error | `done` | P0-03 |
| P1-05 | Offscreen capture + upload | User-triggered record; multipart upload succeeds | `done` | P1-04, P0-04 |
| P1-06 | `POST /api/videos/upload` | Returns videoId; blob in storage | `done` | P0-04, P0-07 |
| P1-07 | Worker: ffmpeg + ASR | Transcript in `transcripts` table | `done` | P0-05, P1-06 |
| P1-08 | Worker: structure analysis | Valid JSON in `video_style_analyses` | `done` | P1-07, P0-08 |
| P1-09 | Task progress + result APIs | Poll shows progress; fetch returns analysis | `done` | P1-07 |
| P1-10 | Side panel UI | Analyze button + report sections render | `done` | P1-05, P1-09 |
| P1-11 | Error handling | Capture/ASR/LLM errors show user messages | `done` | P1-10 |
| P1-12 | Manual E2E (Douyin) | [e2e-checklist.md](../development/e2e-checklist.md) Test A passes | `done` | P1-11 |

**Gate:** P1-12 `done` → Phase 2

---

## Phase 2 — Creator Batch Analysis

| ID | Task | Acceptance | Status | Depends on |
|----|------|------------|--------|------------|
| P2-01 | `extractCreatorProfile()` | Profile fields on Douyin user page | `done` | P1-02 |
| P2-02 | `extractVideoList(limit)` + scroll | Returns N videos from visible DOM | `done` | P2-01 |
| P2-03 | `POST /api/creator-analysis` | Returns taskId; job queued | `done` | P1-09 |
| P2-04 | ANALYZE_CREATOR fan-out | Per-video jobs; progress counters update | `done` | P2-03 |
| P2-05 | Aggregation layer | Stats computed without raw transcript dump | `done` | P1-08 |
| P2-06 | GENERATE_CREATOR_REPORT worker | MD + JSON in `creator_reports` | `done` | P2-05, P0-08 |
| P2-07 | Side panel batch UI | Progress bar + creator report view | `done` | P2-06 |
| P2-08 | Batch E2E | e2e-checklist Test B passes (10 videos) | `done` | P2-07 |

---

## Phase 3 — Visual Analysis

| ID | Task | Acceptance | Status | Depends on |
|----|------|------------|--------|------------|
| P3-01 | Frame extraction worker | Frames in storage; key timestamps covered | `todo` | P1-07 |
| P3-02 | `frame-visual-analysis.md` prompt | Prompt file with JSON output spec | `todo` | P0-08 |
| P3-03 | Vision worker | `visual_analyses` row with frames + summary | `todo` | P3-01, P3-02 |
| P3-04 | Merge vision into structure | Video report includes visual fields | `todo` | P3-03, P1-08 |
| P3-05 | Creator visual aggregation | Subtitle/shooting patterns in aggregation | `todo` | P2-05, P3-04 |
| P3-06 | Report template update | Creator report has shooting/subtitle sections | `todo` | P3-05 |

---

## Phase 4 — Export (V1)

| ID | Task | Acceptance | Status | Depends on |
|----|------|------------|--------|------------|
| P4-01 | Export Markdown | User gets .md from extension or API | `todo` | P2-06 |
| P4-02 | Export JSON | Valid reportJson download | `todo` | P2-06 |
| P4-03 | Export PDF | Readable PDF generated | `todo` | P4-01 |
| P4-06 | EXPORT_REPORT job | Async export with status polling | `todo` | P4-01 |
| P4-04 | Scaffold `apps/web` (Next.js) | — | `deferred` | P0-01 |
| P4-05 | Web report viewer | — | `deferred` | P4-04, P2-06 |

---

## Phase 6 — Production Hardening

| ID | Task | Acceptance | Status | Depends on |
|----|------|------------|--------|------------|
| P6-01 | Extension ↔ API auth | 401 without valid key; upload works with key | `todo` | P1-06 |
| P6-02 | Rate limiting | Excess requests return 429 | `todo` | P6-01 |
| P6-03 | Structured logging | request_id, task_id in API/worker logs | `todo` | P0-04 |
| P6-04 | Retry + dead-letter queue | Failed jobs retry; poison messages isolated | `todo` | P2-04 |
| P6-05 | Media TTL cleanup | Scheduled job deletes expired blobs | `todo` | P1-06 |
| P6-06 | `.env.example` + secrets doc | All env vars documented; no secrets in repo | `todo` | P0-06 |
| P6-07 | GitHub Actions CI | Lint, test, extension build on PR | `todo` | P0-01 |
| P6-08 | Core unit/integration tests | Upload, task status, JSON validation covered | `todo` | P1-08 |
| P6-09 | Staging environment | Full stack deployable; E2E runnable | `todo` | P0-06 |
| P6-10 | Production deploy + rollback | deployment.md has working procedure | `todo` | P6-09 |
| P6-11 | Health + readiness | /health checks DB, Redis, worker heartbeat | `todo` | P6-09 |
| P6-12 | Error monitoring (Sentry) | Test exception appears in dashboard | `todo` | P6-03 |
| P6-13 | AI quota + cost logging | Per-task token/cost logged; limits enforced | `todo` | P1-08 |
| P6-14 | E2E smoke on staging | e2e-checklist Test D passes | `todo` | P2-08 |
| P6-15 | Chrome Web Store package | Zip builds; manifest valid | `todo` | P1-12 |
| P6-16 | Privacy + permission copy | Store-ready policy and permission text | `todo` | P6-15 |
| P6-17 | Security checklist | All items in security.md checked | `todo` | P6-01 |
| P6-18 | **Launch Review** | All launch-criteria.md boxes checked | `todo` | P6-01–17 |

**V1 complete:** P6-18 `done`

---

## Phase 5 — Post-Launch

Not in V1 progress. Start only when user explicitly requests.

| ID | Task | Status | Depends on |
|----|------|--------|------------|
| P5-01 | Second platform adapter (TikTok / Bilibili) | `todo` | P1-02 |
| P5-02 | YouTube Shorts adapter | `todo` | P5-01 |
| P5-03 | Creator comparison view | `todo` | P2-06 |
| P5-04 | Team workspace + auth | `todo` | P4-04 |
| P5-05 | Brand-fit scoring | `todo` | P2-06 |
| P5-06 | Content opportunity discovery | `todo` | P2-06 |
| P5-07 | Script templates from structure | `todo` | P2-06, P0-08 |

---

## Decisions (Locked)

See [architecture/decisions/](../architecture/decisions/README.md).

| ID | Decision | ADR |
|----|----------|-----|
| D-01 | Douyin Web | [001](../architecture/decisions/001-mvp-platform-douyin.md) |
| D-02 | OpenAI STT | [003](../architecture/decisions/003-asr-provider.md) |
| D-03 | Celery + Redis | [002](../architecture/decisions/002-task-queue-celery.md) |
| D-04 | MinIO / R2 / S3 | [004](../architecture/decisions/004-object-storage.md) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-26 | Initial backlog |
| 2026-06-26 | V1 restructure: Phase 6, Douyin lock, Phase 4/5 split, 56 V1 tasks |
| 2026-06-26 | Phase 2 complete (P2-01–P2-08): creator batch analysis pipeline |
