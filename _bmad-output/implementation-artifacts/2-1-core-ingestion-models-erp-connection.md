# Story 2.1: Core Ingestion Models & ERP Connection

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want the core data models for PO lines, snapshots, change events, cross-references, and audit events defined,
so that the ingestion pipeline and all downstream features have a stable data foundation.

## Acceptance Criteria

1. Given the project scaffold and User/Supplier models from Epic 1 exist
   - When the POLine model is defined in `apps/po/models.py`
   - Then it includes fields for: PO number, line number, SKU, item (product family/category), supplier FK, ordered quantity, delivered quantity, remaining quantity, promised date, current status, PO insert date (original creation date), final customer, source quality, last update timestamp, and staleness tracking
   - And it includes 15 physical custom column fields: `custom_date_1` through `custom_date_5` (nullable DateField), `custom_text_1` through `custom_text_5` (nullable CharField), `custom_decimal_1` through `custom_decimal_5` (nullable DecimalField)
   - And it includes a `custom_column_sources` JSONField tracking whether each custom column value is ERP-sourced or user-entered per PO line
   - And a custom manager with `.for_user(user)` method is defined per the RBAC pattern from Story 1.4
2. Given the POLine model exists
   - When the ingestion models are defined in `apps/ingestion/models.py`
   - Then an `ERPSnapshot` model stores: snapshot timestamp, PO line reference data (PO number, line number, SKU, all tracked ERP fields), and a run identifier
   - And an `ERPChangeEvent` model stores: PO line FK (nullable for new lines), field name, previous value, new value, snapshot FK, and detection timestamp
   - And an `ItemXref` model stores: ERP item code, mapped SKU, mapped item (product family), supplier FK, active flag, and timestamps
3. Given the ingestion models exist
   - When the AuditEvent model is defined in `apps/audit/models.py`
   - Then it includes fields for: event_type (string), po_line FK (nullable), user FK (nullable), source (manual/bulk/inline/ingestion/system), timestamp (auto UTC), previous_values (JSON), new_values (JSON), and reason (optional text)
   - And a custom manager overrides `delete()` and `update()` to raise exceptions, enforcing append-only storage per NFR10
   - And a `create_audit_event()` function exists in `apps/core/services.py` as the single entry point for creating audit records
4. Given dual-database routing from Story 1.1 exists
   - When unmanaged ERP models are defined in `apps/ingestion/erp_models.py`
   - Then Django model classes with `managed = False` map to the supplier ERP's PO-related tables
   - And the DatabaseRouter routes these models to the `erp` database connection
   - And no write operations are possible on these models via the ORM
5. Given all models are defined
   - When migrations are generated and applied
   - Then all new tables are created successfully in the app database
   - And no migration attempts to create tables in the ERP database

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
- [x] Task 5: Implement acceptance criteria group 5 (AC: 5)
  - [x] Subtask 5.1: Implement backend/view/template changes required by AC 5
  - [x] Subtask 5.2: Add/adjust tests covering AC 5

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
- Story references path: `apps/audit/models.py`
- Story references path: `apps/core/services.py`
- Story references path: `apps/ingestion/erp_models.py`
- Story references path: `apps/ingestion/models.py`
- Story references path: `apps/po/models.py`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.1)
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

- `_bmad-output/implementation-artifacts/2-1-core-ingestion-models-erp-connection.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 2.1 using the full implementation template format aligned to Story 1.1 structure.
