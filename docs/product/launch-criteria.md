# V1 Launch Criteria

> **V1 is production-ready when every checkbox below is satisfied and P6-18 (Launch Review) is `done`.**

Platform: **Douyin Web** | Product: **Chrome Extension + Backend** | See [ADR 001](../architecture/decisions/001-mvp-platform-douyin.md)

---

## Functional Gates (Phase 1–4)

### Single-video analysis

- [ ] Extension detects Douyin **video** pages correctly
- [ ] User must explicitly click Analyze before any capture starts
- [ ] 30–60s tab capture uploads successfully
- [ ] ASR produces transcript with segments stored in DB
- [ ] Video structure analysis returns validated JSON (hook, structure, tone, template)
- [ ] Side panel displays readable single-video report
- [ ] Capture denied / ASR fail / LLM parse fail show clear user-facing errors

### Creator batch analysis

- [ ] Extension detects Douyin **creator profile** pages
- [ ] User can select sample size (10 / 20 / 50)
- [ ] `extractVideoList` returns visible video metadata
- [ ] Batch job shows progress (`finishedVideos` / `totalVideos`)
- [ ] Creator report aggregates statistics before final LLM pass
- [ ] Side panel displays creator-level report (positioning, hooks, speech, templates)

### Visual analysis

- [ ] Sparse frames extracted (0–5s, middle, last 3–5s prioritized)
- [ ] Vision summary stored in `visual_analyses`
- [ ] Shooting style and subtitle patterns appear in video and creator reports

### Export

- [ ] Export report as Markdown from extension or API
- [ ] Export report as JSON
- [ ] Export report as PDF
- [ ] Export does not include verbatim script clones (structural templates only)

---

## Non-Functional Gates (Phase 6)

### Security & auth

- [ ] Extension ↔ API authenticated (API key or JWT); unauthenticated uploads rejected
- [ ] Rate limiting on upload and analysis endpoints
- [ ] Secrets only via environment variables; `.env.example` documented
- [ ] [security.md](../operations/security.md) checklist fully passed

### Reliability & operations

- [ ] Jobs idempotent on retry (no duplicate DB records)
- [ ] Worker retry policy + dead-letter handling for poison messages
- [ ] Structured logs with `task_id`, `video_id`, `request_id`, step, model, duration
- [ ] `/health` and readiness checks for API, workers, Redis, Postgres
- [ ] Staging environment runs full E2E path
- [ ] Production deployment documented with rollback procedure

### Compliance & data

- [ ] Media TTL cleanup job runs on schedule (no indefinite raw video storage)
- [ ] No silent or background recording
- [ ] Privacy policy and permission explanations ready for Chrome Web Store
- [ ] User-facing copy frames output as learning, not copying

### Quality & CI

- [ ] GitHub Actions: lint, core tests, extension build on PR
- [ ] Core API/worker unit tests for upload, task status, JSON validation
- [ ] Douyin E2E smoke test documented or automated
- [ ] Error monitoring (Sentry or equivalent) configured with DSN

### Cost & limits

- [ ] AI call quota / per-user daily limits enforced
- [ ] Per-task cost logging for ASR and LLM steps

### Store readiness

- [ ] Extension packages cleanly for Chrome Web Store
- [ ] Store listing: description, screenshots, permission justifications
- [ ] Launch Review (P6-18) signed off against this document

---

## Out of Scope for V1

- Multi-platform adapters (TikTok, Bilibili, YouTube Shorts)
- Web dashboard (`apps/web`)
- Team workspace, auth for teams, creator comparison
- Brand-fit scoring, content opportunity discovery

See [Phase 5 backlog](../tasks/phases/phase-5-platform.md) for post-launch items.

## Related

- [PRODUCTION_GATES.md](../tasks/PRODUCTION_GATES.md) — gate-to-task mapping
- [BACKLOG.md](../tasks/BACKLOG.md) — task status
