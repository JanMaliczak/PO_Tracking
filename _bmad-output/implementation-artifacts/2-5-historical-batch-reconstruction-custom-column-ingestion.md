# Story 2.5: Historical Batch Reconstruction & Custom Column Ingestion

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin,
I want historical batch deliveries reconstructed from ERP data and custom columns populated from ERP sources,
so that the application reflects the complete delivery history and extended data fields from day one.

## Acceptance Criteria

1. Given the ERP snapshot contains DeliveredQty and InDate records for PO lines
   - When the batch reconstruction logic in `apps/ingestion/batch_reconstruction.py` runs per FR4
   - Then historical `Batch` records are created in `apps/batches/models.py` from the ERP delivery data
   - And each batch record captures: PO line FK, delivered quantity, delivery date (InDate), and `source='ingestion'`
   - And batch records are linked to their parent PO lines with correct quantity allocation
2. Given historical batches are reconstructed
   - When the reconstruction processes a PO line with multiple delivery records
   - Then separate batch records are created for each distinct delivery event
   - And the cumulative delivered quantity across batches matches the ERP's total DeliveredQty for that PO line
3. Given the admin has configured custom columns with ERP SQL column mappings (via Epic 8, or seed data)
   - When the custom column ingestion in `apps/ingestion/custom_columns.py` runs per FR8b
   - Then up to 15 custom column values (5 date, 5 text, 5 decimal) are extracted from the mapped ERP SQL columns
   - And the corresponding `custom_date_N`, `custom_text_N`, or `custom_decimal_N` fields on the `POLine` record are populated
4. Given custom column values are ingested from the ERP
   - When the source tracking is updated per FR8c
   - Then the `custom_column_sources` field on the `POLine` records the data source as `'erp'` for each ERP-populated custom column
   - And existing user-entered custom column values (source `'user'`) are not overwritten by ERP ingestion

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
- Story references path: `apps/batches/models.py`
- Story references path: `apps/ingestion/batch_reconstruction.py`
- Story references path: `apps/ingestion/custom_columns.py`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.5)
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

- `_bmad-output/implementation-artifacts/2-5-historical-batch-reconstruction-custom-column-ingestion.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 2.5 using the full implementation template format aligned to Story 1.1 structure.
