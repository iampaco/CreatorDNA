# Phase 2 — Creator Batch Analysis

**Goal:** Analyze 10–20 Douyin videos from a creator profile; aggregated creator report.

**Depends on:** Phase 1 complete (P1-12 `done`)  
**V1 tasks:** P2-01 through P2-08

## Acceptance Criteria (phase gate)

- [ ] Creator profile detected on Douyin user page
- [ ] Sample size selection (10 / 20 / 50)
- [ ] Batch progress visible in side panel
- [ ] Creator report uses aggregation-before-LLM pattern
- [ ] [e2e-checklist.md](../../development/e2e-checklist.md) Test B passes

## Task Checklist

### P2-01 — extractCreatorProfile()

**Acceptance:** `CreatorProfile` populated on Douyin user page.

### P2-02 — extractVideoList(limit) + scroll

- [ ] MutationObserver for infinite scroll
- [ ] Dedupe by video URL

**Acceptance:** Returns requested count from visible DOM without duplicate URLs.

### P2-03 — POST /api/creator-analysis

**Acceptance:** Returns `taskId`; validates douyin URLs only in V1.

### P2-04 — ANALYZE_CREATOR fan-out

- [ ] Enqueue per-video jobs via Celery
- [ ] Update `finishedVideos` / `totalVideos`

### P2-05 — Aggregation layer

- [ ] Hook type distribution, topic counts, phrase frequency
- [ ] No concatenation of full transcripts into one LLM call

### P2-06 — GENERATE_CREATOR_REPORT

- [ ] creator-report-generation.md prompt
- [ ] Save `reportMarkdown` + `reportJson`

### P2-07 — Side panel batch UI

- [ ] Progress during batch
- [ ] Creator report view

### P2-08 — Batch E2E

- [ ] e2e-checklist Test B with 10 videos

## Next Phase

P2-08 `done` → [Phase 3](./phase-3-visual.md)
