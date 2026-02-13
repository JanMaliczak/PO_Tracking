# Story 2.3: Snapshot Diff & Change Event Generation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin,
I want the system to detect field-level changes between consecutive ERP snapshots,
so that all PO data changes are tracked with full before/after context.

## Acceptance Criteria

1. Given a current snapshot and a previous snapshot exist for the same ERP data
   - When the diff engine in `apps/ingestion/diff_engine.py` runs
   - Then it compares every field of each PO line record between the two snapshots per FR2
   - And for each field that differs, it generates an `ERPChangeEvent` recording: the PO line reference, field name, previous value, new value, and the snapshot FK per FR3
2. Given the diff engine detects changes
   - When change events are generated
   - Then the corresponding `POLine` records in the app database are updated with the new values from the current snapshot
   - And an audit event is created for each PO line that had changes, with `event_type='ingestion_change'`, `source='ingestion'`, and the previous/new values serialized in JSON
3. Given the diff engine runs
   - When new PO lines appear in the current snapshot that were not in the previous snapshot
   - Then new `POLine` records are created in the app database
   - And an audit event is created for each new PO line with `event_type='po_line_created'` and `source='ingestion'`
4. Given the diff engine runs
   - When PO lines from the previous snapshot are absent from the current snapshot
   - Then the existing `POLine` records are not deleted but may be flagged or status-updated based on business rules
   - And the absence is recorded for ingestion reporting
5. Given the diff engine processes a large dataset
   - When up to 5,000 active PO lines are compared
   - Then the diff operation completes within a reasonable portion of the 1-hour ingestion window per NFR7

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
- Story references path: `apps/ingestion/diff_engine.py`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.3)
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

- `_bmad-output/implementation-artifacts/2-3-snapshot-diff-change-event-generation.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 2.3 using the full implementation template format aligned to Story 1.1 structure.
