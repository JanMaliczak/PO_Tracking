# Story 2.6: Ingestion Orchestration & Results Reporting

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin,
I want the full ingestion pipeline orchestrated as a single management command with comprehensive results reporting,
So that I can schedule nightly runs via SQL Server Agent and verify data health.

## Acceptance Criteria

1. Given all ingestion components (snapshot, diff, xref, batch reconstruction, custom columns) are implemented
   - When the Django management command `run_ingestion` in `apps/ingestion/management/commands/run_ingestion.py` is executed
   - Then it orchestrates the full pipeline in sequence: snapshot extraction -> xref mapping -> diff/change detection -> batch reconstruction -> custom column ingestion -> results reporting
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

- [x] Task 1: Implement end-to-end ingestion management command (AC: 1)
  - [x] Subtask 1.1: Create `run_ingestion` command orchestration flow
  - [x] Subtask 1.2: Add baseline mode (`--baseline`) behavior
- [x] Task 2: Implement results reporting and audit completion/failure events (AC: 2)
  - [x] Subtask 2.1: Build structured run summary payload
  - [x] Subtask 2.2: Log to file and emit ingestion completion/failure audit events
- [x] Task 3: Implement operational resilience and schedule integration (AC: 3, 4)
  - [x] Subtask 3.1: Apply retry/backoff and non-zero exit signaling on hard failures
  - [x] Subtask 3.2: Add `scripts/run_ingestion.bat` for SQL Server Agent usage
- [x] Task 4: Add orchestration regression/performance validation (AC: 1-5)
  - [x] Subtask 4.1: Add command orchestration tests
  - [x] Subtask 4.2: Add reporting payload and failure-path tests
  - [x] Subtask 4.3: Run tests and Django checks

## Dev Notes

- Keep orchestration step order stable; this command is the integration backbone.
- Ensure error handling preserves observability and operational triage quality.

### Project Structure Notes

- Command: `apps/ingestion/management/commands/run_ingestion.py`
- Wrapper: `scripts/run_ingestion.bat`

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.6)
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/prd.md`

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- `.venv/bin/python manage.py test apps.ingestion.tests.test_run_ingestion_command --settings=po_tracking.settings.development -v 2`
- `.venv/bin/python manage.py test --settings=po_tracking.settings.development -v 1`
- `.venv/bin/python manage.py check --settings=po_tracking.settings.development`

### Completion Notes List

- Added end-to-end ingestion management command at `apps/ingestion/management/commands/run_ingestion.py` that runs the pipeline in stable order: snapshot extraction (including xref stage accounting) → diff/change detection (unless `--baseline`) → historical batch reconstruction → custom column ingestion → results reporting.
- Added `--baseline` mode in `run_ingestion` to skip diff processing and treat baseline-created lines as the `new_lines_created` count for reporting.
- Implemented structured run summary payload with required FR6 metrics: duration, processed lines, new lines, change events, reconstructed batches, custom columns populated, xref gaps, unmapped codes, and errors.
- Added audit event emission for pipeline outcomes: `ingestion_completed` on success and `ingestion_failed` on failure, each recorded immediately with structured payload.
- Added hard-failure signaling in command execution (`CommandError`) to ensure non-zero exit codes for SQL Server Agent failure detection, while preserving observability via failure audit + exception log.
- Added scheduling wrapper `scripts/run_ingestion.bat` for Windows/SQL Server Agent usage with virtualenv activation and production settings invocation.
- Added command-level regression tests in `apps/ingestion/tests/test_run_ingestion_command.py` for normal flow orchestration, baseline diff-skip behavior, and failure-path audit/exit behavior.
- Verified full regression suite and Django checks pass after changes (103 tests passing).

### File List

- `apps/ingestion/management/__init__.py`
- `apps/ingestion/management/commands/__init__.py`
- `apps/ingestion/management/commands/run_ingestion.py`
- `apps/ingestion/tests/test_run_ingestion_command.py`
- `scripts/run_ingestion.bat`
- `_bmad-output/implementation-artifacts/2-6-ingestion-orchestration-results-reporting.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-02-13: Implemented Story 2.6 ingestion orchestration command with baseline mode, structured reporting payload, success/failure audit events, non-zero failure signaling, SQL Server Agent wrapper script, and command regression tests; status moved to `review`.
- 2026-02-13: Code review fixes applied — H1: moved `logger.exception` before unguarded `create_audit_event` in failure path and wrapped audit write in try/except to prevent masking original exception; H2: replaced empty `run_identifier=""` with `pending-{uuid}` fallback so failure audit events are always traceable; M1: added `absent_po_lines` assertion to success test; M2: added post-snapshot partial-failure test verifying `run_identifier` is populated in failure payload; M3: added stdout JSON parsing test; M4: added `--baseline` failure path test; L1: removed redundant `bool()` cast; 106 tests passing; status moved to `done`.
