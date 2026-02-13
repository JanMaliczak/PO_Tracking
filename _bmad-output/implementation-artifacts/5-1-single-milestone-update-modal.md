# Story 5.1: Single Milestone Update Modal

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a expeditor,
I want to record a milestone date update for a single PO line with required context,
so that planners have an accurate, sourced, and explained update for their decision-making.

## Acceptance Criteria

1. Given an expeditor is viewing the PO list or detail panel for a PO line within their supplier scope
   - When they click the update milestone action on a single PO line
   - Then a modal dialog opens via HTMX loading the `po/_milestone_modal.html` fragment
   - And the modal displays the PO line context (PO number, line, SKU, supplier, current promised date)
2. Given the milestone modal is open
   - When the form is displayed per FR22
   - Then it contains fields for: milestone type (production-ready or ready-to-dispatch), new date (date picker), reason (text input), source classification (dropdown), and optional free-text notes per FR27
   - And all three mandatory fields (date, reason, source) are clearly marked as required per FR23
3. Given the expeditor selects a source classification per FR24
   - When they choose from the dropdown
   - Then the options are: "Supplier confirmed", "Expeditor estimate", and "No supplier response"
   - And the selected source will be stored with the milestone update
4. Given the expeditor fills all required fields and submits
   - When the form passes validation
   - Then the PO line's milestone date is updated in the database
   - And an append-only audit event is created via `create_audit_event()` with: `event_type='milestone_updated'`, `source='manual'`, user FK, previous date, new date, reason, source quality, and notes per FR26
   - And the modal closes via `closeModal` HTMX trigger
   - And the table row refreshes to reflect the updated date and source quality badge
   - And a success toast notification is displayed
5. Given the expeditor submits with missing required fields per FR23
   - When validation fails
   - Then the modal form is re-rendered with inline error messages indicating which fields are missing
   - And the submission is rejected and no database update or audit event is created
   - And the modal remains open for correction
6. Given a planner or unauthorized user attempts to access the milestone update action
   - When the request is processed
   - Then it is rejected with HTTP 403 per FR40 and the RBAC enforcement from Story 1.4

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
- Story references path: `po/_milestone_modal.html`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 5, Story 5.1)
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

- `_bmad-output/implementation-artifacts/5-1-single-milestone-update-modal.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 5.1 using the full implementation template format aligned to Story 1.1 structure.
