# Production Gates ↔ Task Mapping

Each launch criterion maps to backlog tasks. Check off gates in [launch-criteria.md](../product/launch-criteria.md) when the linked tasks are `done`.

## Functional Gates

| Gate | Tasks |
|------|-------|
| Single-video E2E | P1-03, P1-05, P1-07, P1-08, P1-10, P1-11, P1-12 |
| Creator batch E2E | P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08 |
| Visual analysis in reports | P3-01, P3-03, P3-04, P3-05, P3-06 |
| Export MD / JSON / PDF | P4-01, P4-02, P4-03, P4-06 |

## Non-Functional Gates

| Gate | Tasks |
|------|-------|
| API auth | P6-01 |
| Rate limiting | P6-02 |
| Structured logging | P6-03 |
| Job retry + DLQ | P6-04 |
| Media TTL cleanup | P6-05 |
| Secrets / env docs | P6-06 |
| CI pipeline | P6-07 |
| Core unit tests | P6-08 |
| Staging environment | P6-09 |
| Production deploy + rollback | P6-10 |
| Health / readiness | P6-11 |
| Error monitoring | P6-12 |
| AI quota + cost logs | P6-13 |
| E2E smoke | P6-14 |
| Extension store package | P6-15 |
| Privacy / permission copy | P6-16 |
| Security checklist | P6-17 |
| **Final Launch Review** | **P6-18** |

## Launch Review Procedure (P6-18)

1. Open [launch-criteria.md](../product/launch-criteria.md)
2. Verify every checkbox can be honestly marked complete
3. Run [e2e-checklist.md](../development/e2e-checklist.md) on staging
4. Confirm [runbooks.md](../operations/runbooks.md) covers top 5 failure modes
5. Mark P6-18 `done` in [BACKLOG.md](./BACKLOG.md) and update [STATUS.md](../STATUS.md)

**V1 complete = P6-18 `done`.**
