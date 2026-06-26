# Phase 6 — Production Hardening

**Goal:** Security, observability, CI/CD, staging, and store readiness for formal launch.

**Depends on:** Phase 4 export tasks complete  
**V1 tasks:** P6-01 through P6-18  
**V1 complete when:** P6-18 Launch Review is `done`

## Acceptance Criteria (phase gate)

- [ ] All [launch-criteria.md](../../product/launch-criteria.md) checkboxes satisfied
- [ ] [PRODUCTION_GATES.md](../PRODUCTION_GATES.md) mapping verified
- [ ] [security.md](../../operations/security.md) checklist complete
- [ ] Staging E2E (e2e-checklist Test D) passes

## Task Checklist

### Security & auth

| ID | Task | Acceptance |
|----|------|------------|
| P6-01 | API auth | 401 without key; extension upload works with key |
| P6-02 | Rate limiting | 429 after threshold |
| P6-17 | Security audit | All security.md items checked |

### Reliability

| ID | Task | Acceptance |
|----|------|------------|
| P6-03 | Structured logging | Fields per observability.md |
| P6-04 | Retry + DLQ | Retries work; poison job isolated |
| P6-05 | Media TTL | Blobs deleted after retention window |
| P6-11 | Health checks | /health fails if DB/Redis down |

### DevOps

| ID | Task | Acceptance |
|----|------|------------|
| P6-06 | .env.example | Documented in getting-started.md |
| P6-07 | GitHub Actions | PR checks pass on clean branch |
| P6-08 | Tests | Core paths covered per testing-strategy.md |
| P6-09 | Staging | Full stack deployed |
| P6-10 | Prod deploy | deployment.md + rollback tested |

### Monitoring & cost

| ID | Task | Acceptance |
|----|------|------------|
| P6-12 | Sentry | Test error captured |
| P6-13 | AI quotas | Limits enforced; cost per task logged |

### Launch

| ID | Task | Acceptance |
|----|------|------------|
| P6-14 | Staging E2E | e2e-checklist Test D |
| P6-15 | Store package | Valid zip for Chrome Web Store |
| P6-16 | Privacy copy | Permission justifications documented |
| P6-18 | Launch Review | launch-criteria.md fully checked |

## Launch Review Procedure (P6-18)

1. Walk [launch-criteria.md](../../product/launch-criteria.md) line by line
2. Run [e2e-checklist.md](../../development/e2e-checklist.md) on staging
3. Confirm [runbooks.md](../../operations/runbooks.md) has real commands
4. Mark P6-18 `done`; update [STATUS.md](../../STATUS.md) to V1 complete

## After V1

Post-launch features → [Phase 5](./phase-5-platform.md)
