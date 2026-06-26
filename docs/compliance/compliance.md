# Compliance & Safety

These rules are **mandatory** for all features and copy. Violations block merge.

## Technical Constraints

1. Do not bypass login, paywalls, privacy restrictions, DRM, or platform access controls.
2. Do not scrape private or non-public content.
3. Do not present the product as a video downloader.
4. Do not store full original videos longer than necessary for analysis.
5. Do not use hidden or silent recording.
6. Always require **explicit user action** before tab capture or media recording.

## Content & AI Constraints

7. Do not generate direct clones of a creator's exact scripts, catchphrases, or identity.
8. Do not encourage impersonation of specific creators.
9. Prefer analyzing **structure, style, and patterns** over copying content.
10. Use `safety-rewrite.md` when generating user-facing suggestions from analysis.

## User-Facing Copy

**Use:**

> CreatorDNA helps users understand public content patterns and generate original content strategies inspired by structural analysis.

**Avoid:**

> Copy this creator's exact style.

## Extension-Specific

| Requirement | Implementation |
|-------------|----------------|
| No silent capture | Analyze button must start recording |
| Visible consent | Browser permission prompts are expected |
| Session-bound data | Only collect from active tab user opened |
| Temp media retention | Delete blobs after pipeline completes (configurable TTL) |

## Chrome Web Store (P6-15, P6-16)

| Requirement | Notes |
|-------------|-------|
| Privacy policy | Disclose audio sent to ASR provider; data retention TTL |
| Permission justification | tabCapture for user-initiated analysis only |
| No misleading claims | "Learn patterns" not "copy creator" |
| Single purpose | Creator style intelligence, not downloader |

See [security.md](../operations/security.md) for permission table.

## Agent Checklist (before PR)

- [ ] No new code records without user gesture
- [ ] No wording implying plagiarism or impersonation
- [ ] Generated templates are structural, not verbatim
- [ ] Media retention policy documented if storage logic added

## Related

- [launch-criteria.md](../product/launch-criteria.md)
- [Vision & Outcomes](../product/vision-and-outcomes.md)
- [AGENTS.md — Compliance](../../AGENTS.md#compliance-and-safety-rules)
