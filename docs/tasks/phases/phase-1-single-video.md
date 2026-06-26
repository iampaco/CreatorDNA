# Phase 1 — Single Video MVP (Douyin Web)

**Goal:** One Douyin video → user-triggered capture → ASR → structure report in side panel.

**Platform:** Douyin Web only ([ADR 001](../../architecture/decisions/001-mvp-platform-douyin.md))  
**V1 tasks:** P1-01 through P1-12  
**Gate:** P1-12 `done` before Phase 2

## Acceptance Criteria (phase gate)

- [ ] Douyin video page detected; creator page classified separately
- [ ] Analyze only works after explicit user click
- [ ] Transcript + structure JSON in database
- [ ] Side panel report readable
- [ ] [e2e-checklist.md](../../development/e2e-checklist.md) Test A passes

## Test URLs (fill when running E2E)

| Type | URL |
|------|-----|
| Video | `https://www.douyin.com/video/<record-id>` |
| Creator | `https://www.douyin.com/user/<record-id>` |

## Task Checklist

### P1-01 — PlatformAdapter interface

- [ ] `packages/platform-core` exports interface
- [ ] Methods: `detectPage`, `extractCreatorProfile`, `extractVideoList`, `extractCurrentVideo`

### P1-02 — douyin-web.adapter.ts

- [ ] URL patterns for video and user pages
- [ ] Layered DOM extraction for current video
- [ ] HTML fixture tests optional but recommended

**Acceptance:** Returns `CreatorVideoMeta` on open Douyin video tab.

### P1-03 — Content script

- [ ] Select adapter by hostname
- [ ] Message passing to background on detection/metadata

### P1-04 — Background state machine

- [ ] States: idle → capturing → uploading → processing → done | error
- [ ] Persist in `chrome.storage`

### P1-05 — Offscreen capture

- [ ] tabCapture stream ID flow
- [ ] MediaRecorder 30–60s limit
- [ ] Multipart upload to API

**Acceptance:** webm blob reaches storage; no capture without user gesture.

### P1-06 — Upload API

- [ ] `POST /api/videos/upload` with Pydantic validation
- [ ] Store blob; return `videoId`

### P1-07 — ASR pipeline

- [ ] ffmpeg webm → 16kHz WAV
- [ ] OpenAI STT per [ADR 003](../../architecture/decisions/003-asr-provider.md)
- [ ] Save to `transcripts`

### P1-08 — Structure analysis

- [ ] Load video-structure-analysis.md prompt
- [ ] Validate LLM JSON; save `video_style_analyses`

### P1-09 — Progress + result APIs

- [ ] `GET /api/tasks/:taskId`
- [ ] `GET /api/videos/:videoId/analysis`

### P1-10 — Side panel UI

- [ ] Analyze button (disabled on unsupported pages)
- [ ] Progress + report sections

### P1-11 — Error handling

- [ ] capture_denied, asr_failed, llm_parse_failed user messages

### P1-12 — E2E

- [ ] Complete e2e-checklist Test A; record URLs and date

## Next Phase

P1-12 `done` → [Phase 2](./phase-2-creator-batch.md)
