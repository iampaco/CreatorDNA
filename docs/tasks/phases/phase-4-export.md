# Phase 4 — Export (V1)

**Goal:** Export creator reports as Markdown, JSON, and PDF from extension or API.

**Depends on:** Phase 2 (P2-06)  
**V1 tasks:** P4-01, P4-02, P4-03, P4-06 (active)  
**Deferred:** P4-04, P4-05 (Web dashboard — post-V1)

## Acceptance Criteria (phase gate)

- [ ] Markdown export downloads or copies correctly
- [ ] JSON export matches `reportJson` schema
- [ ] PDF is human-readable
- [ ] EXPORT_REPORT job supports async generation
- [ ] e2e-checklist Test C export rows pass

## Task Checklist

### P4-01 — Export Markdown

**Acceptance:** User triggers export; receives valid .md file.

### P4-02 — Export JSON

**Acceptance:** Downloaded JSON validates against schema.

### P4-03 — Export PDF

**Acceptance:** PDF renders report sections without truncation.

### P4-06 — EXPORT_REPORT job

**Acceptance:** Job enqueued; poll until `completed`; file URL or download.

## Deferred (Post-V1)

| ID | Task | Notes |
|----|------|-------|
| P4-04 | Scaffold `apps/web` | Next.js dashboard |
| P4-05 | Web report viewer | Depends on P4-04 |

## Next Phase

P4-01–03, P4-06 `done` → [Phase 6 Production](./phase-6-production.md)
