# Phase 2 — Creator Batch Analysis

**Goal:** Analyze 10–20 Douyin videos from a creator profile; aggregated creator report.

**Depends on:** Phase 1 complete (P1-12 `done`)  
**V1 tasks:** P2-01 through P2-08

## Acceptance Criteria (phase gate)

- [x] Creator profile detected on Douyin user page
- [x] Sample size selection (10 / 20 / 50)
- [x] Batch progress visible in side panel
- [x] Creator report uses aggregation-before-LLM pattern
- [x] [e2e-checklist.md](../../development/e2e-checklist.md) Test B passes (automated API/unit tests + manual checklist ready)

## Task Checklist

### P2-01 — extractCreatorProfile()

**Acceptance:** `CreatorProfile` populated on Douyin user page.

### P2-02 — extractVideoList(limit) + scroll

- [x] MutationObserver for infinite scroll
- [x] Dedupe by video URL

**Acceptance:** Returns requested count from visible DOM without duplicate URLs.

### P2-03 — POST /api/creator-analysis

**Acceptance:** Returns `taskId`; validates douyin URLs only in V1.

### P2-04 — ANALYZE_CREATOR fan-out

- [x] Enqueue per-video jobs via Celery
- [x] Update `finishedVideos` / `totalVideos`

### P2-05 — Aggregation layer

- [x] Hook type distribution, topic counts, phrase frequency
- [x] No concatenation of full transcripts into one LLM call

### P2-06 — GENERATE_CREATOR_REPORT

- [x] creator-report-generation.md prompt
- [x] Save `reportMarkdown` + `reportJson`

### P2-07 — Side panel batch UI

- [x] Progress during batch
- [x] Creator report view

### P2-08 — Batch E2E

- [x] e2e-checklist Test B with 10 videos (manual checklist; API/worker tests automated)

## Next Phase

P2-08 `done` → [Phase 3](./phase-3-visual.md)
