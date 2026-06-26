# Phase 3 — Visual Analysis

**Goal:** Frame extraction and vision understanding merged into video and creator reports.

**Depends on:** Phase 2 recommended; P3-01 can start after P1-07  
**V1 tasks:** P3-01 through P3-06

## Acceptance Criteria (phase gate)

- [ ] Frames extracted at key timestamps (0–5s, middle, end)
- [ ] `visual_analyses` populated per video
- [ ] Creator report includes shooting style and subtitle consistency

## Task Checklist

### P3-01 — Frame extraction

```bash
ffmpeg -i input.webm -vf fps=1/3 frames/frame_%04d.jpg
```

**Acceptance:** Frames in object storage; sparse set covers hook and ending.

### P3-02 — frame-visual-analysis.md prompt

**Acceptance:** Prompt specifies JSON fields per AGENTS.md frame example.

### P3-03 — Vision worker

**Acceptance:** Per-frame + summary JSON in `visual_analyses`.

### P3-04 — Merge into structure analysis

**Acceptance:** Video-level report includes shooting/subtitle from vision.

### P3-05 — Creator visual aggregation

**Acceptance:** Aggregated subtitle position/style patterns across videos.

### P3-06 — Report template update

**Acceptance:** Creator report sections 7–8 (shooting, subtitle) populated.

## Next Phase

P3-06 `done` → [Phase 4](./phase-4-export.md)
