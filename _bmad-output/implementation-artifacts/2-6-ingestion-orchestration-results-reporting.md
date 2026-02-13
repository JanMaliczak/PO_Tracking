# Story 2.6: Ingestion Orchestration & Results Reporting

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin,
I want the full ingestion pipeline orchestrated as a single management command with comprehensive results reporting,
so that I can schedule nightly runs via SQL Server Agent and verify data health.

## Acceptance Criteria

1. Given all ingestion components (snapshot, diff, xref, batch reconstruction, custom columns) are implemented
   - When the Django management command `run_ingestion` in `apps/ingestion/management/commands/run_ingestion.py` is executed
   - Then it orchestrates the full pipeline in sequence: snapshot extraction → xref mapping → diff/change detection → batch reconstruction → custom column ingestion → results reporting
   - And the command accepts a `--baseline` flag for first-run mode (skip diff, treat all as new) per FR5
   - And the command is callable via `manage.py run_ingestion --settings=po_tracking.settings.production`
2. Given the ingestion pipeline completes (success or partial failure)
   - When results are reported per FR6
   - Then the report includes: run duration, PO lines processed, new lines created, change events detected, batches reconstructed, custom columns populated, xref gaps found, and errors encountered
   - And the results are logged to both file-based logging and an audit event with `event_type='ingestion_completed'` or `event_type='ingestion_failed'`
   - And the audit event is written within 60 seconds of pipeline completion per NFR29
3. Given the ingestion command runs
   - When transient ERP connection errors occur during execution
   - Then retry logic with configurable attempts and backoff is applied per NFR19
   - And if retries are exhausted, the pipeline logs a failure event and exits with a non-zero exit code for SQL Server Agent to detect
4. Given the ingestion pipeline is designed for scheduling
   - When a `scripts/run_ingestion.bat` wrapper script exists
   - Then it activates the virtual environment and invokes the management command with the production settings module
   - And it is suitable for execution by SQL Server Agent as a nightly scheduled job
5. Given the ingestion pipeline runs nightly
   - When performance is measured
   - Then the full pipeline (snapshot, diff, change events, batch reconstruction, custom columns) completes within 1 hour for up to 5,000 active PO lines per NFR7

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
- Story references path: `apps/ingestion/management/commands/run_ingestion.py`
- Story references path: `scripts/run_ingestion.bat`

### Testing Requirements

- Add unit/integration tests for acceptance criteria behavior and authorization boundaries.
- Add HTMX response tests for fragment endpoints where relevant.
- Verify regression safety for role scoping, validation rules, and business state transitions.

### Latest Tech Information

- Keep implementation compatible with current architecture-pinned stack versions in planning artifacts.
- If upgrading a dependency, validate compatibility with `mssql-django` and document rationale before applying.

### Project Context Reference

- Primary source story definition: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.6)
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

- `_bmad-output/implementation-artifacts/2-6-ingestion-orchestration-results-reporting.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/planning-artifacts/prd.md`

## Review Follow-ups (AI)

- [ ] [AI-Review][HIGH] Validate implementation against all acceptance criteria before marking story complete.
- [ ] [AI-Review][MEDIUM] Add/confirm test coverage for role scoping, validation, and HTMX response paths.
- [ ] [AI-Review][LOW] Keep documentation sections synchronized with any implementation changes.

## Change Log

- 2026-02-13: Regenerated Story 2.6 using the full implementation template format aligned to Story 1.1 structure.
