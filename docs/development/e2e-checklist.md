# Douyin E2E Checklist

Manual acceptance template. Complete for **P1-12** (single video), **P2-08** (batch), and **P6-14** (staging smoke).

## Environment

| Field | Value |
|-------|-------|
| Date | |
| Tester | |
| Extension version | |
| API URL | |
| Environment | local / staging / production |

## Preconditions

- [ ] Logged into Douyin Web (if required for target content)
- [ ] Extension loaded and side panel opens
- [ ] API `/health` returns OK
- [ ] Celery worker running

---

## Test A: Single Video Analysis (P1-12)

**Test URL:** `https://www.douyin.com/video/<id>` (record actual URL used)

| Step | Expected | Pass |
|------|----------|------|
| Open video page | Extension shows "supported" / Analyze enabled | |
| Open side panel | UI loads without console errors | |
| Click Analyze | Browser prompts for capture permission (if first time) | |
| Wait for capture | Recording indicator visible; stops at limit | |
| Upload + processing | Progress updates in side panel | |
| Report displayed | Hook, structure, speaking style sections present | |
| No silent capture | Recording only after button click | |

**Errors to verify (optional runs):**

| Scenario | Expected |
|----------|----------|
| Deny capture permission | Clear error message, return to idle |
| Unsupported page (e.g. google.com) | Analyze disabled or explanatory message |

---

## Test B: Creator Batch Analysis (P2-08)

**Test URL:** `https://www.douyin.com/user/<id>` (record actual URL used)

| Step | Expected | Pass |
|------|----------|------|
| Open creator profile | Creator name detected | |
| Select sample size (10) | Video list populated from visible DOM | |
| Start batch analysis | Progress: N/10 videos | |
| All videos complete | Creator report in side panel | |
| Report content | Positioning, hooks, templates (not verbatim scripts) | |

---

## Test C: Visual + Export (Phase 3–4)

| Step | Expected | Pass |
|------|----------|------|
| Run batch or single with vision enabled | Shooting/subtitle sections in report | |
| Export Markdown | File downloads / copies correctly | |
| Export JSON | Valid JSON matching schema | |
| Export PDF | Readable PDF generated | |

---

## Test D: Staging Smoke (P6-14)

Repeat Test A and Test B against **staging** API URL with production-like config.

| Check | Pass |
|-------|------|
| Auth required (no key → 401) | |
| Media cleaned up after TTL (spot-check storage) | |
| Sentry receives test error (if configured) | |

---

## Sign-off

- [ ] All required tests passed
- [ ] Issues logged in BACKLOG if failures found
- [ ] Ready for P6-18 Launch Review
