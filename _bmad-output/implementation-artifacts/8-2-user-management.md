# Story 8.2: User Management

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin,
I want to create, edit, and deactivate user accounts with role assignment and supplier scope,
so that I can control who has access to the system and what data they can see.

## Acceptance Criteria

1. Given an admin navigates to the User Management page at `/admin-portal/users/`
   - When the page renders (`admin_portal/user_list.html`)
   - Then a list of all user accounts is displayed with: username, full name, role, assigned supplier (for expeditors), active status, and last login date
   - And the list supports sorting and filtering by role and active status
2. Given the admin clicks "Create User"
   - When the user form loads via HTMX (`admin_portal/_user_form.html` fragment) per FR41
   - Then the form contains fields for: username, password, first name, last name, role (dropdown: admin/planner/expeditor), and active status
   - And all required fields are validated on submission
3. Given the admin selects the "expeditor" role on the user form
   - When the role is selected per FR42
   - Then a supplier scope assignment field appears (dropdown or multi-select of available suppliers)
   - And at least one supplier must be assigned for an expeditor
4. Given the admin submits a valid new user form
   - When the user is created
   - Then a new User record is created with the specified role, supplier assignment (if expeditor), and active status
   - And the password is stored using PBKDF2 hashing per NFR8
   - And an audit event is created with `event_type='user_created'`, `source='manual'`, and the admin user
   - And a success toast notification is displayed
   - And the user list refreshes to include the new user
5. Given the admin clicks "Edit" on an existing user
   - When the edit form loads per FR41
   - Then it is pre-populated with the user's current data
   - And the admin can modify role, supplier scope, name, and active status
   - And password can be reset but the current password is not displayed
6. Given the admin deactivates a user per FR41
   - When the user's active status is set to false
   - Then the user can no longer log in
   - And existing sessions for that user are invalidated
   - And an audit event is created with `event_type='user_deactivated'`
   - And the user record is preserved (not deleted) for audit history integrity
7. Given the admin modifies an expeditor's supplier scope per FR42
   - When the supplier assignment is changed
   - Then the user's data access scope changes immediately on their next request
   - And an audit event records the previous and new supplier assignments

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
- Story references path: `admin_portal/_user_form.html`
- Story references path: `admin_portal/user_list.html`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.2)
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

- `_bmad-output/implementation-artifacts/8-2-user-management.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 8.2 using the full implementation template format aligned to Story 1.1 structure.
