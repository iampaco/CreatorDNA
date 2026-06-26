# Phase 4 Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable creator report export as Markdown, JSON, and PDF from extension side panel and API, with async EXPORT_REPORT job for PDF generation.

**Architecture:** Reuse existing `creator_reports` data. Sync GET endpoints serve MD/JSON directly. POST `/api/reports/{creatorId}/export` enqueues Celery `export_report_task` (required for PDF; optional for MD/JSON). Export files stored in object storage under `exports/{task_id}/`. Task polling via existing `GET /api/tasks/{taskId}` extended with `downloadUrl`. Extension uses client-side Blob download for MD/JSON and async poll+download for PDF.

**Tech Stack:** FastAPI, Celery, reportlab (PDF), boto3/MinIO, WXT extension

---

## Task 1: Export DB model + migration

**Files:**
- Create: `apps/api/db/models/export_task.py`
- Modify: `apps/api/db/models/__init__.py`
- Create: `alembic/versions/004_export_tasks.py`

- [ ] Add `ExportTask` model: `id`, `creator_id`, `report_id`, `format`, `status`, `progress`, `object_key`, `error_code`, `error_message`, timestamps
- [ ] Alembic migration for `export_tasks` table
- [ ] Register model in `__init__.py`

## Task 2: Export schemas + service

**Files:**
- Create: `apps/api/schemas/export.py`
- Create: `apps/api/services/export.py`
- Modify: `apps/api/schemas/task.py` — add `downloadUrl` optional field

- [ ] `ExportFormat` enum: `markdown`, `json`, `pdf`
- [ ] `CreateExportRequest`, `CreateExportResponse`
- [ ] `ExportService.create_export()`, `get_report_for_export()`, `get_download_bytes()`
- [ ] Validate `reportJson` via reused `parse_report_json` logic

## Task 3: PDF generation service

**Files:**
- Create: `workers/services/pdf_export.py`
- Modify: `pyproject.toml` — add `reportlab`

- [ ] `markdown_to_pdf_bytes(markdown: str) -> bytes` using reportlab Platypus
- [ ] Parse `#` headings, render body text with Chinese font fallback

## Task 4: EXPORT_REPORT Celery worker

**Files:**
- Create: `workers/tasks/export_report.py`
- Modify: `workers/celery_app.py`
- Modify: `apps/api/services/storage.py` — `build_export_key()`

- [ ] `export_report_task` generates file, uploads to storage, updates `ExportTask`
- [ ] Register task in celery `include`

## Task 5: API routes

**Files:**
- Create: `apps/api/routers/exports.py`
- Modify: `apps/api/main.py`
- Modify: `apps/api/services/analysis.py` — resolve `ExportTask` in `resolve_task_response`

- [ ] `GET /api/reports/{creator_id}/export/markdown` — sync MD download
- [ ] `GET /api/reports/{creator_id}/export/json` — sync JSON download
- [ ] `POST /api/reports/{creator_id}/export` — enqueue async export
- [ ] `GET /api/exports/{task_id}/download` — fetch completed file

## Task 6: Shared types + extension

**Files:**
- Modify: `packages/shared-types/src/task.ts`, `report.ts`
- Create: `apps/extension/lib/download.ts`
- Modify: `apps/extension/lib/api-client.ts`
- Modify: `apps/extension/entrypoints/sidepanel/main.ts`, `style.css`
- Modify: `apps/extension/lib/messages.ts` — export message types

- [ ] Export buttons: Markdown, JSON, PDF
- [ ] MD/JSON client-side Blob download
- [ ] PDF: POST export → poll task → download

## Task 7: Tests + docs

**Files:**
- Create: `tests/test_export.py`
- Modify: `docs/tasks/BACKLOG.md`, `docs/STATUS.md`, `docs/tasks/phases/phase-4-export.md`
- Modify: `docs/api/api.md`, `docs/api/schemas.md`

- [ ] API tests for sync export and async enqueue
- [ ] PDF generation unit test
- [ ] Mark P4-01–03, P4-06 done
