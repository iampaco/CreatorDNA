# ADR 003: ASR Provider — OpenAI Speech-to-Text

**Status:** Accepted  
**Date:** 2026-06-26  
**Deciders:** Engineering

## Context

V1 requires reliable Mandarin transcription for Douyin content. ASR runs server-side after ffmpeg extracts 16 kHz mono WAV from captured audio.

## Decision

V1 default ASR provider: **OpenAI Speech-to-Text API** (Whisper-based).

- Store `asr_model` on `transcripts` records
- Output format per AGENTS.md: segments with `start`, `end`, `text`
- API key via environment variable; never commit secrets

### Switch conditions (to local Whisper / faster-whisper)

Consider migrating when **any** of:

- Monthly ASR cost exceeds budget threshold (see P6-13 cost logging)
- Latency SLO consistently missed
- Offline / air-gapped deployment required

Document provider change in a new ADR; keep `asr_model` field for audit.

## Consequences

**Positive**

- High quality for zh-CN without GPU ops in V1
- Simple integration path for MVP
- Faster time-to-first-transcript

**Negative**

- Per-minute API cost and external dependency
- Audio leaves infra to third-party API (document in privacy policy)

## Alternatives Considered

| Option | Rejected for V1 because |
|--------|-------------------------|
| Local Whisper | GPU/CPU ops and model hosting not in Phase 0 scope |
| faster-whisper | Same; defer until cost/latency triggers |
| Platform captions only | Unreliable; not always visible in browser session |

## References

- [pipeline.md](../../ai-pipeline/pipeline.md)
- [P1-07 in BACKLOG](../../tasks/BACKLOG.md)
