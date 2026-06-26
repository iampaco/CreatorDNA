# Testing Strategy

Layered testing for V1. Agents should add tests when implementing tasks marked with test expectations.

## Pyramid

```txt
        ┌─────────────┐
        │  E2E Manual │  P1-12, P2-08, P6-14, launch-criteria
        │  + Smoke    │
        ├─────────────┤
        │ Integration │  API + DB + Redis (P6-08)
        ├─────────────┤
        │  Unit       │  Adapters, validators, aggregation (P6-08)
        └─────────────┘
```

## By Layer

### Unit tests

| Area | What to test | When |
|------|--------------|------|
| `platform-adapters` | URL detection, metadata parsing from HTML fixtures | P1-02 |
| Pydantic schemas | Valid/invalid request bodies | P0-04 |
| JSON validators | LLM output → schema | P1-08 |
| Aggregation | Stats from mock video analyses | P2-05 |

**Tools:** Vitest (TS), pytest (Python)

### Integration tests

| Area | What to test | When |
|------|--------------|------|
| Upload API | Multipart store + DB row | P1-06 |
| Task progress | State transitions | P1-09 |
| Celery task | Mock ASR/LLM, real Redis | P6-08 |

Run against docker-compose services in CI.

### E2E

| Flow | Type | Task |
|------|------|------|
| Single video | Manual checklist on real Douyin page | P1-12 |
| Creator batch | Manual 10-video run | P2-08 |
| Full staging | Manual or Playwright smoke | P6-14 |

Use [e2e-checklist.md](./e2e-checklist.md) for manual runs.

## CI (P6-07)

On every PR to `main`:

```txt
pnpm lint
pnpm test          # packages + extension unit
pytest apps/api tests/
pytest workers/tests/
pnpm --filter extension build
```

Block merge on failure.

## What Not to Test in V1

- Live Douyin DOM in CI (too brittle; use HTML fixtures)
- Real OpenAI calls in CI (mock providers)
- Chrome tabCapture in headless CI (manual or staging only)

## Agent Rule

When marking a task `done`, note in PR or BACKLOG whether tests were added. P6-08 requires core tests before launch.

## Related

- [e2e-checklist.md](./e2e-checklist.md)
- [launch-criteria.md](../product/launch-criteria.md)
