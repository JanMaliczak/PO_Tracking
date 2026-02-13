# Story 7.1: Supplier Excel Generation & Download

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a expeditor,
I want to generate and download a structured Excel file for a selected supplier containing all their open PO lines,
so that I can send suppliers a professional, pre-filled request file instead of manually building spreadsheets.

## Acceptance Criteria

1. Given an expeditor is viewing the PO list filtered to a specific supplier
   - When they click a "Generate Supplier Excel" action per FR34
   - Then the system generates an Excel file containing all open PO lines for that supplier
   - And the file is downloaded to the user's browser as an `.xlsx` file
   - And the filename includes the supplier name and generation date (e.g., `SupplierName_PO_Request_2026-02-13.xlsx`)
2. Given the Excel file is being generated per FR35
   - When the data is populated
   - Then the file is pre-filled with columns for: PO number, item (product family/category), SKU, ordered quantity, remaining quantity, promised date, current status, and final customer
   - And data is sourced from the current database state using `.for_user(request.user)` scoping
   - And rows are sorted by promised date ascending (most urgent first)
3. Given the Excel file is generated using `openpyxl` in `apps/exports/generators.py`
   - When the file formatting is applied
   - Then the header row is styled with bold text and a distinct background color for readability
   - And date columns are formatted as dates (not text strings)
   - And numeric columns (quantities) are formatted as numbers
   - And column widths are auto-adjusted for content readability
4. Given a supplier has up to 200 open PO lines
   - When the Excel generation completes
   - Then the file is generated and download begins within 5 seconds per NFR4
5. Given a supplier has zero open PO lines
   - When the expeditor attempts to generate an Excel file
   - Then a warning message indicates there are no open PO lines for the selected supplier
   - And no empty file is generated
6. Given a planner or unauthorized user attempts to generate a supplier Excel
   - When the request is processed
   - Then it is rejected with HTTP 403 per RBAC enforcement from Story 1.4

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

## Dev Notes

### Developer Context Section

- This story belongs to Epic 7 and should align implementation to the PRD, architecture, and UX artifacts.
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
- Story references path: `apps/exports/generators.py`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 7, Story 7.1)
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

- `_bmad-output/implementation-artifacts/7-1-supplier-excel-generation-download.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 7.1 using the full implementation template format aligned to Story 1.1 structure.
