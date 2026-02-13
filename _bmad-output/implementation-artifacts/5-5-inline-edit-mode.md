# Story 5.5: Inline Edit Mode

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a expeditor,
I want to edit milestone fields directly in the PO list table across multiple rows with different values per row,
so that I can quickly enter row-specific updates without opening modals for each line.

## Acceptance Criteria

1. Given the PO list view is displayed for an expeditor
   - When the expeditor activates inline edit mode per FR27b
   - Then editable milestone columns (milestone date, reason, source, ready quantity, notes) become inline input fields on each visible PO line row
   - And the `po/_inline_edit_row.html` fragment replaces the standard row rendering
   - And the `static/js/inline-edit.js` script manages activation/deactivation of edit mode
2. Given inline edit mode is active
   - When the expeditor enters values across multiple rows
   - Then each row can have different values for date, reason, source, ready quantity, and notes
   - And rows with changes are visually highlighted to distinguish them from unchanged rows
   - And mandatory fields (date, reason, source) are validated per-row per FR23
3. Given the expeditor has entered values across multiple rows
   - When they click a "Submit All Changes" action
   - Then all modified rows are submitted as a batch to the server
   - And each modified PO line is updated with its row-specific values
   - And an audit event is created for each modified PO line with `source='inline'` per FR26
   - And a success toast shows the count of rows updated
   - And inline edit mode deactivates and the table returns to normal display
4. Given inline edit mode is active
   - When the expeditor clicks "Cancel" or presses Escape
   - Then all unsaved changes are discarded
   - And the table rows revert to their normal read-only display
   - And no database updates or audit events are created
5. Given inline edit validation fails on one or more rows
   - When the batch submission is processed
   - Then rows with validation errors display inline error indicators
   - And valid rows are committed successfully (partial success)
   - And the expeditor can correct and resubmit failed rows
6. Given inline edit mode renders input fields
   - When accessibility is verified
   - Then all input fields are labeled per NFR26
   - And tab navigation moves between editable fields in logical order
   - And the edit mode state is announced to screen readers

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

- This story belongs to Epic 5 and should align implementation to the PRD, architecture, and UX artifacts.
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
- Story references path: `po/_inline_edit_row.html`
- Story references path: `static/js/inline-edit.js`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 5, Story 5.5)
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

- `_bmad-output/implementation-artifacts/5-5-inline-edit-mode.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 5.5 using the full implementation template format aligned to Story 1.1 structure.
