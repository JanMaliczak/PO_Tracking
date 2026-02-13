# Story 6.2: Batch Status Lifecycle

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a expeditor,
I want to update batch status through a defined lifecycle,
so that planners can track the progress of each shipment from planning through delivery.

## Acceptance Criteria

1. Given the batch status lifecycle is defined per FR31
   - When the status model is implemented
   - Then valid batch statuses are: Planned, Confirmed, Dispatched, Delivered
   - And valid transitions are enforced:
   - - Planned to Confirmed
   - - Confirmed to Dispatched
   - - Dispatched to Delivered
2. Given an expeditor views a batch in the PO detail panel batch list
   - When a status transition action is available
   - Then only valid next statuses are presented as options based on the current status
   - And invalid transitions are not offered in the UI
3. Given the expeditor selects a valid status transition
   - When the transition is submitted
   - Then the batch status is updated in the database
   - And an audit event is created with `event_type='batch_status_changed'`, previous status, new status, batch FK, PO line FK, user, and source
   - And the batch row in the detail panel refreshes to show the new status badge
   - And a success toast notification is displayed
4. Given a batch transitions to "Dispatched"
   - When the transition is processed
   - Then the dispatched quantity is reflected in the PO line's quantity tracking (dispatched total increases)
   - And the Quantity Progress Display in the detail panel updates accordingly
5. Given a batch transitions to "Delivered"
   - When the transition is processed
   - Then the delivered quantity is reflected in the PO line's quantity tracking (delivered total increases)
   - And if cumulative delivered quantity across all batches equals the ordered quantity, the system suggests transitioning the PO line status to "Fully Delivered" per Story 5.6
   - And if partial, the PO line status may transition to "Part Delivered"
6. Given an invalid batch status transition is attempted
   - When the transition is rejected
   - Then a validation error message indicates the allowed transitions from the current status
   - And no database update or audit event is created

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

- This story belongs to Epic 6 and should align implementation to the PRD, architecture, and UX artifacts.
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

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 6, Story 6.2)
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

- `_bmad-output/implementation-artifacts/6-2-batch-status-lifecycle.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 6.2 using the full implementation template format aligned to Story 1.1 structure.
