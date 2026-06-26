# ADR 002: Task Queue — Celery + Redis

**Status:** Accepted  
**Date:** 2026-06-26  
**Deciders:** Engineering

## Context

Analysis jobs are long-running (media upload, ffmpeg, ASR, LLM). The API must enqueue work and return task IDs for progress polling. Workers are Python (ffmpeg, AI clients).

## Decision

Use **Celery** with **Redis** as broker and result backend.

- Job types per AGENTS.md: `ANALYZE_VIDEO`, `TRANSCRIBE_AUDIO`, `GENERATE_CREATOR_REPORT`, etc.
- Redis also used for short-lived task state and caching
- Workers run as separate processes/containers from FastAPI

## Consequences

**Positive**

- Mature Python ecosystem for media/AI workers
- Built-in retries, routing, and monitoring hooks
- Aligns with FastAPI + Python worker stack in AGENTS.md

**Negative**

- Operational complexity vs. in-process background tasks
- Requires Redis availability in all environments

## Alternatives Considered

| Option | Rejected because |
|--------|------------------|
| BullMQ | TypeScript-native; workers are Python |
| FastAPI BackgroundTasks | No persistence, retries, or fan-out for batch jobs |
| Temporal | Over-engineered for V1 scope |

## References

- [overview.md](../overview.md)
- [data-flow.md](../data-flow.md)
