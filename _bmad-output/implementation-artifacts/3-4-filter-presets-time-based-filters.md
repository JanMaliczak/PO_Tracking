# Story 3.4: Filter Presets & Time-Based Filters

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a planner,
I want preset filter views for common exception scenarios and time-based filters,
so that I can jump directly to late, at-risk, recently updated, or stale PO lines with one click.

## Acceptance Criteria

1. Given the PO list view is displayed
   - When the Filter Preset Navigation component is rendered
   - Then preset tabs are displayed for: "All", "Late", "At Risk", "Updated Recently", "No Response" per FR16
   - And the tabs follow the UX spec's Filter Preset Navigation component design
   - And "All" is the default active tab
2. Given the user clicks the "Late" preset tab
   - When the preset is applied
   - Then the table body refreshes via HTMX to show only PO lines with a promised date in the past
   - And the "Late" tab is visually highlighted as active
3. Given the user clicks the "At Risk" preset tab
   - When the preset is applied
   - Then the table shows PO lines within the configurable at-risk threshold of their due date
4. Given the user clicks the "Updated Recently" preset tab
   - When the preset is applied per FR14
   - Then the table shows PO lines updated within a specified time window (e.g., last 24 hours)
   - And this supports cross-timezone awareness so planners can see what expeditors updated during their working hours
5. Given the user clicks the "No Response" preset tab
   - When the preset is applied per FR15
   - Then the table shows PO lines with no expeditor update within the configurable staleness threshold
6. Given a filter preset is active
   - When the user applies additional column filters on top of the preset
   - Then both the preset filter and column filters are applied together (AND logic)
   - And clearing all filters returns to the "All" view
7. Given filter presets trigger HTMX partial refresh
   - When any preset tab is clicked
   - Then only the table body swaps via `_table_body.html` fragment
   - And the response completes within 2 seconds per NFR2

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

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.4)
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

- `_bmad-output/implementation-artifacts/3-4-filter-presets-time-based-filters.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 3.4 using the full implementation template format aligned to Story 1.1 structure.
