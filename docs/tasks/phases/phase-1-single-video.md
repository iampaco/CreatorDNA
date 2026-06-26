# Phase 1 — Single Video MVP (Douyin Web)

**Goal:** One Douyin video → user-triggered capture → ASR → structure report in side panel.

**Platform:** Douyin Web only ([ADR 001](../../architecture/decisions/001-mvp-platform-douyin.md))  
**V1 tasks:** P1-01 through P1-12  
**Gate:** P1-12 `done` before Phase 2

## Acceptance Criteria (phase gate)

- [x] Douyin video page detected; creator page classified separately
- [x] Analyze only works after explicit user click
- [x] Transcript + structure JSON in database
- [x] Side panel report readable
- [x] Automated API/worker tests pass; manual [e2e-checklist.md](../../development/e2e-checklist.md) Test A ready

## Test URLs (fill when running E2E)

| Type | URL |
|------|-----|
| Video | `https://www.douyin.com/video/<record-id>` |
| Creator | `https://www.douyin.com/user/<record-id>` |

## Task Checklist

### P1-01 — PlatformAdapter interface

- [x] `packages/platform-core` exports interface
- [x] Methods: `detectPage`, `extractCreatorProfile`, `extractVideoList`, `extractCurrentVideo`

### P1-02 — douyin-web.adapter.ts

- [x] URL patterns for video and user pages
- [x] Layered DOM extraction for current video
- [x] HTML fixture tests optional but recommended

**Acceptance:** Returns `CreatorVideoMeta` on open Douyin video tab.

### P1-03 — Content script

- [x] Select adapter by hostname
- [x] Message passing to background on detection/metadata

### P1-04 — Background state machine

- [x] States: idle → capturing → uploading → processing → done | error
- [x] Persist in `chrome.storage`

### P1-05 — Offscreen capture

- [x] tabCapture stream ID flow
- [x] MediaRecorder 30–60s limit
- [x] Multipart upload to API

**Acceptance:** webm blob reaches storage; no capture without user gesture.

### P1-06 — Upload API

- [x] `POST /api/videos/upload` with Pydantic validation
- [x] Store blob; return `videoId`

### P1-07 — ASR pipeline

- [x] ffmpeg webm → 16kHz WAV
- [x] OpenAI STT per [ADR 003](../../architecture/decisions/003-asr-provider.md)
- [x] Save to `transcripts`

### P1-08 — Structure analysis

- [x] Load video-structure-analysis.md prompt
- [x] Validate LLM JSON; save `video_style_analyses`

### P1-09 — Progress + result APIs

- [x] `GET /api/tasks/:taskId`
- [x] `GET /api/videos/:videoId/analysis`

### P1-10 — Side panel UI

- [x] Analyze button (disabled on unsupported pages)
- [x] Progress + report sections

### P1-11 — Error handling

- [x] capture_denied, asr_failed, llm_parse_failed user messages

### P1-12 — E2E

- [x] Automated tests (`pytest tests/`); manual e2e-checklist Test A template ready

## Next Phase

P1-12 `done` → [Phase 2](./phase-2-creator-batch.md)
