# Story 8.1: Admin Dashboard & Navigation

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin,
I want a central admin portal with navigation to all administrative functions and health summary,
so that I can quickly assess system status and navigate to the area that needs attention.

## Acceptance Criteria

1. Given an admin is logged in
   - When they navigate to `/admin-portal/`
   - Then the admin dashboard page is rendered (`admin_portal/dashboard.html`)
   - And it is accessible only to users with the `admin` role via `@role_required('admin')`
2. Given the admin dashboard is displayed
   - When the navigation is rendered
   - Then links are provided to: User Management, Xref Management, Ingestion Monitor, Audit Log, System Configuration, and Custom Column Configuration
   - And the navigation follows the Direction B visual design with the dark blue navbar
3. Given the admin dashboard is displayed
   - When summary health indicators are rendered
   - Then the dashboard shows: last ingestion run status and timestamp, count of unmapped xref items, count of active users by role, and replication status (if applicable)
   - And indicators use color plus icon plus text for status (healthy/warning/error) per NFR25
4. Given a non-admin user attempts to access `/admin-portal/`
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
- Story references path: `admin_portal/dashboard.html`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.1)
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

- `_bmad-output/implementation-artifacts/8-1-admin-dashboard-navigation.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 8.1 using the full implementation template format aligned to Story 1.1 structure.
