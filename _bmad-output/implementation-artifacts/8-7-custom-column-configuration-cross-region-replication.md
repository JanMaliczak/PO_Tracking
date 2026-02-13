# Story 8.7: Custom Column Configuration & Cross-Region Replication

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin,
I want to configure custom columns and monitor cross-region data replication status,
so that I can extend the data model for operational needs and ensure European users have current data.

## Acceptance Criteria

1. Given an admin navigates to Custom Column Configuration at `/admin-portal/custom-columns/`
   - When the page renders (`admin_portal/custom_columns.html`) per FR49
   - Then a list of all 15 custom column slots is displayed: 5 date-type, 5 text-type, 5 decimal-type
   - And each slot shows: slot number, current display label (or "Unconfigured"), data type, data source (ERP or user-entered), default visibility per role, and active/inactive status
2. Given the admin clicks to configure a custom column slot
   - When the configuration form loads via HTMX (`admin_portal/_custom_column_form.html`) per FR49
   - Then the form contains fields for: display label, data source (ERP SQL column mapping or user-entered), and default visibility per role (checkboxes for expeditor/planner/admin)
   - And the data type is fixed by the slot (date/text/decimal) and displayed as read-only
3. Given the admin configures a custom column with ERP source
   - When the ERP SQL column mapping is specified per FR49
   - Then a field allows entering the ERP SQL column name to map to this custom column
   - And the mapping will be used by the ingestion pipeline to populate the column from ERP data
4. Given the admin submits a valid custom column configuration
   - When the configuration is saved
   - Then a `CustomColumnConfig` record is created or updated
   - And an audit event is created with `event_type='custom_column_configured'`
   - And the column becomes available in the PO list column chooser and detail panel
   - And a success toast confirms the update
5. Given the admin activates or deactivates a custom column per FR50
   - When the active status is toggled
   - Then deactivated columns are hidden from the PO list column chooser and all views
   - And existing data in deactivated columns is preserved in the database (not deleted)
   - And reactivating a column restores visibility with all previous data intact
   - And an audit event records the activation/deactivation
6. Given the system uses cross-region replication per FR8
   - When the admin dashboard renders replication status
   - Then the last successful replication timestamp is displayed
   - And if replication has not completed within the expected nightly window (10:00-07:00 UTC per NFR21), a warning indicator is shown
   - And on replication failure, the European instance serves the last successful sync data and an admin alert audit event is generated per NFR22
7. Given the European instance is serving stale data
   - When a user on the European instance accesses the application
   - Then a staleness banner is displayed via `_partials/_staleness_banner.html` indicating the data age
   - And the `StalenessMiddleware` in `apps/core/middleware.py` detects and injects the banner for the European deployment

## Tasks / Subtasks

- [ ] Task 1: Implement acceptance criteria group 1 (AC: 1)
  - [ ] Subtask 1.1: Implement backend/view/template changes required by AC 1
  - [ ] Subtask 1.2: Add/adjust tests covering AC 1
- [ ] Task 2: Implement acceptance criteria group 2 (AC: 2)
  - [ ] Subtask 2.1: Implement backend/view/template changes required by AC 2
  - [ ] Subtask 2.2: Add/adjust tests covering AC 2
- [ ] Task 3: Implement acceptance criteria group 3 (AC: 3)
  - [ ] Subtask 3.1: Implement backend/view/template changes required by AC 3
  - [ ] Subtask 3.2: Add/adjust tests covering AC 3
- [ ] Task 4: Implement acceptance criteria group 4 (AC: 4)
  - [ ] Subtask 4.1: Implement backend/view/template changes required by AC 4
  - [ ] Subtask 4.2: Add/adjust tests covering AC 4
- [ ] Task 5: Implement acceptance criteria group 5 (AC: 5)
  - [ ] Subtask 5.1: Implement backend/view/template changes required by AC 5
  - [ ] Subtask 5.2: Add/adjust tests covering AC 5
- [ ] Task 6: Implement acceptance criteria group 6 (AC: 6)
  - [ ] Subtask 6.1: Implement backend/view/template changes required by AC 6
  - [ ] Subtask 6.2: Add/adjust tests covering AC 6
- [ ] Task 7: Implement acceptance criteria group 7 (AC: 7)
  - [ ] Subtask 7.1: Implement backend/view/template changes required by AC 7
  - [ ] Subtask 7.2: Add/adjust tests covering AC 7

## Dev Notes

### Developer Context Section

- This story belongs to Epic 8 and should align implementation to the PRD, architecture, and UX artifacts.
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
- Story references path: `admin_portal/_custom_column_form.html`
- Story references path: `admin_portal/custom_columns.html`
- Story references path: `apps/core/middleware.py`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.7)
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

- Story context generated in full template format and prepared for developer execution.
- Acceptance criteria mapped into actionable tasks and guardrails for implementation consistency.

### File List

- `_bmad-output/implementation-artifacts/8-7-custom-column-configuration-cross-region-replication.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 8.7 using the full implementation template format aligned to Story 1.1 structure.
