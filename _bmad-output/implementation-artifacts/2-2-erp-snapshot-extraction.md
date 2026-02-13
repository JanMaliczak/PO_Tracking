# Story 2.2: ERP Snapshot Extraction

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin,
I want the system to connect to the supplier ERP and extract a complete snapshot of active PO line data,
so that the application has a current baseline of all PO information for change detection.

## Acceptance Criteria

1. Given the ERP database connection is configured and the unmanaged ERP models exist
   - When the snapshot extraction runs in `apps/ingestion/snapshot.py`
   - Then it connects to the supplier ERP using read-only SQL credentials per NFR11
   - And it extracts all active PO line records including: PO number, line number, SKU/item codes, ordered quantity, delivered quantity, promised date, status fields, Item (product family/category), PO insert date (original PO creation date), and final customer per FR1 and FR8a
   - And each extracted record is stored as an `ERPSnapshot` row linked to the current run identifier
2. Given a snapshot extraction is in progress
   - When the ERP connection encounters a transient error
   - Then the extraction retries with configurable retry count and backoff delay per NFR19
   - And if all retries fail, the extraction halts and logs a failure event
3. Given a snapshot extraction completes successfully
   - When the results are reviewed
   - Then the snapshot contains all active PO lines from the ERP with no write-back to the ERP per NFR20
   - And the snapshot timestamp and record count are recorded for reporting
4. Given this is the first-ever ingestion run (no previous snapshot exists)
   - When the snapshot extraction runs in baseline mode per FR5
   - Then all extracted records are treated as new PO lines without change detection
   - And POLine records are created in the app database from the baseline snapshot
   - And an audit event is logged recording the baseline initialization

## Tasks / Subtasks

- [x] Task 1: Implement acceptance criteria group 1 (AC: 1)
  - [x] Subtask 1.1: Implement backend/view/template changes required by AC 1
  - [x] Subtask 1.2: Add/adjust tests covering AC 1
- [x] Task 2: Implement acceptance criteria group 2 (AC: 2)
  - [x] Subtask 2.1: Implement backend/view/template changes required by AC 2
  - [x] Subtask 2.2: Add/adjust tests covering AC 2
- [x] Task 3: Implement acceptance criteria group 3 (AC: 3)
  - [x] Subtask 3.1: Implement backend/view/template changes required by AC 3
  - [x] Subtask 3.2: Add/adjust tests covering AC 3
- [x] Task 4: Implement acceptance criteria group 4 (AC: 4)
  - [x] Subtask 4.1: Implement backend/view/template changes required by AC 4
  - [x] Subtask 4.2: Add/adjust tests covering AC 4

## Dev Notes

### Developer Context Section

- This story belongs to Epic 2 and should align implementation to the PRD, architecture, and UX artifacts.
- Keep scope constrained to the acceptance criteria above; avoid introducing unrelated behavior changes.
- Prefer iterative delivery with HTMX partial updates and server-rendered templates where interaction requires dynamic updates.

### Technical Requirements

- Implement exactly the behaviors required by the acceptance criteria and preserve role-based data scoping.
- Use Django model/view/form/template patterns that match existing project structure.
- Ensure write operations that affect business state emit append-only audit events where applicable.
- Preserve performance expectations for list/detail views and partial updates as defined in NFRs.

### Architecture Compliance

- Follow architecture boundaries in `_bmad-output/planning-artifacts/architecture.md` (views orchestrate, services handle business logic, managers/querysets enforce scoping).
- Keep HTMX responses in underscore-prefixed template fragments for partial swaps.
- Enforce RBAC at endpoint and queryset levels (`@role_required`, `.for_user(request.user)`).
- Maintain append-only principles for audit/event history updates.

### Library Framework Requirements

- Runtime stack alignment: Django 5.2.x, `mssql-django 1.6`, `django-htmx 1.27.0`, Bootstrap 5.3.x patterns, `openpyxl` for export flows.
- Do not introduce SPA frameworks or alternate backend patterns that conflict with the architecture document.

### File Structure Requirements

- Follow established app boundaries under `apps/` and template fragments under `templates/`.
- Story references path: `apps/ingestion/snapshot.py`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.2)
- Architecture guardrails: `_bmad-output/planning-artifacts/architecture.md`
- UX requirements and interaction patterns: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Requirement baseline: `_bmad-output/planning-artifacts/prd.md`

### Project Structure Notes

- Alignment with unified project structure (paths, modules, naming).
- Note and justify any detected variances before implementation.

### References

- Cite all technical details with source paths and sections, e.g. [Source: docs/<file>.md#Section]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

### Completion Notes List

- Story document upgraded to full implementation template format while preserving `done` status.
- Acceptance criteria and task mapping retained from epic source with implementation guardrails sections added.

### File List

- `_bmad-output/implementation-artifacts/2-2-erp-snapshot-extraction.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 2.2 using the full implementation template format aligned to Story 1.1 structure.
