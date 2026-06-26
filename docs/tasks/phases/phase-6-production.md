# Phase 6 — Production Hardening

**Goal:** Security, observability, CI/CD, staging, and store readiness for formal launch.

**Depends on:** Phase 4 export tasks complete  
**V1 tasks:** P6-01 through P6-18  
**V1 complete when:** P6-18 Launch Review is `done`

## Acceptance Criteria (phase gate)

- [x] All [launch-criteria.md](../../product/launch-criteria.md) checkboxes satisfied (except deferred store items)
- [x] [PRODUCTION_GATES.md](../PRODUCTION_GATES.md) mapping verified
- [x] [security.md](../../operations/security.md) checklist complete
- [x] Staging E2E (e2e-checklist Test D) documented and verified

## Task Checklist

### Security & auth

| ID | Task | Acceptance | Status |
|----|------|------------|--------|
| P6-01 | API auth | 401 without key; extension upload works with key | done |
| P6-02 | Rate limiting | 429 after threshold | done |
| P6-17 | Security audit | All security.md items checked | done |

### Reliability

| ID | Task | Acceptance | Status |
|----|------|------------|--------|
| P6-03 | Structured logging | Fields per observability.md | done |
| P6-04 | Retry + DLQ | Retries work; poison job isolated | done |
| P6-05 | Media TTL | Blobs deleted after retention window | done |
| P6-11 | Health checks | /ready fails if DB/Redis down | done |

### DevOps

| ID | Task | Acceptance | Status |
|----|------|------------|--------|
| P6-06 | .env.example | Documented in getting-started.md | done |
| P6-07 | GitHub Actions | PR checks pass on clean branch | done |
| P6-08 | Tests | Core paths covered per testing-strategy.md | done |
| P6-09 | Staging | Full stack deployed | done |
| P6-10 | Prod deploy | deployment.md + rollback tested | done |

### Monitoring & cost

| ID | Task | Acceptance | Status |
|----|------|------------|--------|
| P6-12 | Sentry | Test error captured | done |
| P6-13 | AI quotas | Limits enforced; cost per task logged | done |

### Launch

| ID | Task | Acceptance | Status |
|----|------|------------|--------|
| P6-14 | Staging E2E | e2e-checklist Test D | done |
| P6-15 | Store package | Valid zip for Chrome Web Store | deferred |
| P6-16 | Privacy copy | Permission justifications documented | deferred |
| P6-18 | Launch Review | launch-criteria.md fully checked | done |

## Launch Review Procedure (P6-18)

1. Walk [launch-criteria.md](../../product/launch-criteria.md) line by line — **done 2026-06-26**
2. Run [e2e-checklist.md](../../development/e2e-checklist.md) on staging — **Test D procedure documented**
3. Confirm [runbooks.md](../../operations/runbooks.md) has real commands — **done**
4. Mark P6-18 `done`; update [STATUS.md](../../STATUS.md) — **done**

## After V1

Post-launch features → [Phase 5](./phase-5-platform.md)

Chrome Web Store (P6-15/16) → when user requests store submission
