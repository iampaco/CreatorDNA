# V1 Launch Criteria

> **V1 is production-ready when every checkbox below is satisfied and P6-18 (Launch Review) is `done`.**

Platform: **Douyin Web** | Product: **Chrome Extension + Backend** | See [ADR 001](../architecture/decisions/001-mvp-platform-douyin.md)

---

## Functional Gates (Phase 1–4)

### Single-video analysis

- [x] Extension detects Douyin **video** pages correctly
- [x] User must explicitly click Analyze before any capture starts
- [x] 30–60s tab capture uploads successfully
- [x] ASR produces transcript with segments stored in DB
- [x] Video structure analysis returns validated JSON (hook, structure, tone, template)
- [x] Side panel displays readable single-video report
- [x] Capture denied / ASR fail / LLM parse fail show clear user-facing errors

### Creator batch analysis

- [x] Extension detects Douyin **creator profile** pages
- [x] User can select sample size (10 / 20 / 50)
- [x] `extractVideoList` returns visible video metadata
- [x] Batch job shows progress (`finishedVideos` / `totalVideos`)
- [x] Creator report aggregates statistics before final LLM pass
- [x] Side panel displays creator-level report (positioning, hooks, speech, templates)

### Visual analysis

- [x] Sparse frames extracted (0–5s, middle, last 3–5s prioritized)
- [x] Vision summary stored in `visual_analyses`
- [x] Shooting style and subtitle patterns appear in video and creator reports

### Export

- [x] Export report as Markdown from extension or API
- [x] Export report as JSON
- [x] Export report as PDF
- [x] Export does not include verbatim script clones (structural templates only)

---

## Non-Functional Gates (Phase 6)

### Security & auth

- [x] Extension ↔ API authenticated (API key or JWT); unauthenticated uploads rejected
- [x] Rate limiting on upload and analysis endpoints
- [x] Secrets only via environment variables; `.env.example` documented
- [x] [security.md](../operations/security.md) checklist fully passed

### Reliability & operations

- [x] Jobs idempotent on retry (no duplicate DB records)
- [x] Worker retry policy + dead-letter handling for poison messages
- [x] Structured logs with `task_id`, `video_id`, `request_id`, step, model, duration
- [x] `/health` and readiness checks for API, workers, Redis, Postgres
- [x] Staging environment runs full E2E path
- [x] Production deployment documented with rollback procedure

### Compliance & data

- [x] Media TTL cleanup job runs on schedule (no indefinite raw video storage)
- [x] No silent or background recording
- [ ] Privacy policy and permission explanations ready for Chrome Web Store *(deferred P6-16)*
- [x] User-facing copy frames output as learning, not copying

### Quality & CI

- [x] GitHub Actions: lint, core tests, extension build on PR
- [x] Core API/worker unit tests for upload, task status, JSON validation
- [x] Douyin E2E smoke test documented or automated
- [x] Error monitoring (Sentry or equivalent) configured with DSN

### Cost & limits

- [x] AI call quota / per-user daily limits enforced
- [x] Per-task cost logging for ASR and LLM steps

### Store readiness

- [ ] Extension packages cleanly for Chrome Web Store *(deferred P6-15)*
- [ ] Store listing: description, screenshots, permission justifications *(deferred P6-16)*
- [x] Launch Review (P6-18) signed off against this document

---

## Out of Scope for V1

- Multi-platform adapters (TikTok, Bilibili, YouTube Shorts)
- Web dashboard (`apps/web`)
- Team workspace, auth for teams, creator comparison
- Brand-fit scoring, content opportunity discovery
- Chrome Web Store submission (P6-15/16 deferred per product decision)

See [Phase 5 backlog](../tasks/phases/phase-5-platform.md) for post-launch items.

## Related

- [PRODUCTION_GATES.md](../tasks/PRODUCTION_GATES.md) — gate-to-task mapping
- [BACKLOG.md](../tasks/BACKLOG.md) — task status
