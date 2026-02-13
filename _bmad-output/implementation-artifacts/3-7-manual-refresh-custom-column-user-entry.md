# Story 3.7: Manual Refresh & Custom Column User Entry

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want to manually refresh the PO list data and edit user-entered custom column values inline,
so that I see the latest data on demand and can maintain extended fields without leaving the list view.

## Acceptance Criteria

1. Given the PO list view is displayed
   - When the user clicks the manual refresh action per FR17
   - Then the current view data is reloaded from the server via HTMX partial refresh
   - And all active filters, sort order, and pagination position are preserved
   - And the refresh button shows a loading indicator during the request
   - And the refreshed data reflects the latest database state
2. Given a PO line has user-entered custom columns (source is not ERP-mapped)
   - When the user clicks to edit a custom column value inline in the PO list view per FR51
   - Then the cell becomes an editable input field appropriate to the column type: date picker for date columns, text input for text columns, numeric input for decimal columns
   - And the inline edit follows the UX spec's inline edit interaction pattern
3. Given the user enters or updates a custom column value inline
   - When the value is submitted
   - Then the `POLine` record is updated with the new value
   - And the `custom_column_sources` field records the source as `'user'` for that column per FR8c
   - And an audit event is created with `event_type='custom_column_updated'`, `source='inline'`, and the previous/new values
   - And a success toast notification is displayed
   - And the table row refreshes to show the updated value
4. Given the user attempts to edit a custom column that is ERP-sourced
   - When the cell is rendered
   - Then it is displayed as read-only and cannot be edited inline
   - And a visual indicator distinguishes ERP-sourced values from user-entered values
5. Given inline edit validation fails
   - When an invalid value is entered (e.g., non-date text in a date column)
   - Then the input shows inline validation feedback
   - And the submission is rejected until a valid value is provided
   - And no audit event is created for a rejected submission

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

## Dev Notes

### Developer Context Section

- This story belongs to Epic 3 and should align implementation to the PRD, architecture, and UX artifacts.
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

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.7)
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

- `_bmad-output/implementation-artifacts/3-7-manual-refresh-custom-column-user-entry.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 3.7 using the full implementation template format aligned to Story 1.1 structure.
