# Task System

## Purpose

Track **what is done**, **what is next**, and **what blocks what** so AI agents and humans can pick work without re-reading the entire `AGENTS.md`.

## V1 vs Post-Launch

| Track | Phases | Tasks | Complete when |
|-------|--------|-------|---------------|
| **V1** | 0, 1, 2, 3, 4, 6 | 56 | P6-18 Launch Review |
| Post-launch | 5 | 7 | Not in V1 progress |

See [launch-criteria.md](../product/launch-criteria.md) for production gates.

## Files

| File | Role |
|------|------|
| [STATUS.md](../STATUS.md) | One-page progress — update every task |
| [BACKLOG.md](./BACKLOG.md) | Master checklist with acceptance column |
| [PRODUCTION_GATES.md](./PRODUCTION_GATES.md) | Launch gates ↔ task mapping |
| [phases/](./phases/) | Per-phase acceptance checklists |

## Task Status Values

| Status | Meaning |
|--------|---------|
| `todo` | Not started |
| `in_progress` | Actively being worked |
| `blocked` | Waiting on dependency or decision |
| `done` | Complete and verified |
| `deferred` | Postponed (e.g. P4-04 web dashboard) |

## How Agents Should Use This

1. Read [STATUS.md](../STATUS.md) for next task ID.
2. Pick lowest V1 phase with unblocked `todo` items.
3. Read the phase file for acceptance criteria.
4. Implement per [module-ownership.md](../architecture/module-ownership.md).
5. Mark `done` in BACKLOG, phase file, and STATUS.

## Priority Order (V1)

```txt
Phase 0: Foundation
    ↓
Phase 1: Single video (Douyin)
    ↓
Phase 2: Creator batch
    ↓
Phase 3: Visual analysis
    ↓
Phase 4: Export (not web dashboard)
    ↓
Phase 6: Production hardening → LAUNCH
    ↓
Phase 5: Post-launch (optional)
```

Do not skip phases unless the user explicitly requests a spike.
