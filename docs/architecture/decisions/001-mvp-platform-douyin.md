# ADR 001: MVP Platform — Douyin Web

**Status:** Accepted  
**Date:** 2026-06-26  
**Deciders:** Product / Engineering

## Context

CreatorDNA V1 targets a single complete vertical slice: browser extension + backend + AI pipeline for one short-video platform. Multi-platform support increases adapter maintenance and E2E test surface before core pipeline is proven.

## Decision

V1 will support **Douyin Web** (`www.douyin.com`) only.

- First platform adapter: `apps/extension/platform-adapters/douyin-web.adapter.ts`
- All E2E and launch criteria reference Douyin pages
- TikTok, Bilibili, YouTube Shorts deferred to Phase 5 (post-launch)

## Consequences

**Positive**

- Faster path to production launch on one DOM/URL model
- Clear test baseline for agents and QA
- Adapter interface (`PlatformAdapter`) remains platform-agnostic for future adapters

**Negative**

- Non-Douyin users cannot use V1
- Douyin DOM changes require adapter updates

## Alternatives Considered

| Option | Rejected because |
|--------|------------------|
| TikTok Web first | Product chose Douyin for V1 target market |
| Douyin + TikTok in V1 | Violates "one platform first" MVP principle in AGENTS.md |
| Headless crawler | Violates compliance: browser-assisted, user-triggered only |

## References

- [vision-and-outcomes.md](../../product/vision-and-outcomes.md)
- [phase-1-single-video.md](../../tasks/phases/phase-1-single-video.md)
