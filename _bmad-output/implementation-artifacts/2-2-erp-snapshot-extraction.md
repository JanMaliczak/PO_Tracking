# Story 2.2: ERP Snapshot Extraction

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin,
I want the system to connect to the supplier ERP and extract a complete snapshot of active PO line data,
So that the application has a current baseline of all PO information for change detection.

## Acceptance Criteria

1. Given the ERP database connection is configured and the unmanaged ERP models exist
   - When the snapshot extraction runs in `apps/ingestion/snapshot.py`
   - Then it connects to the supplier ERP using read-only SQL credentials per NFR11
   - And it extracts all active PO line records including: PO number, line number, SKU/item codes, ordered quantity, delivered quantity, promised date, status fields, Item (product family/category), PO insert date (original PO creation date), and final customer per FR1 and FR8a
   - And each extracted record is stored as an `ERPSnapshot` row linked to the current run identifier
2. Given a snapshot extraction is in progress
   - When the ERP connection encounters a transient error
   - Then the extraction retries with configurable retry count and backoff delay per NFR19
   - And if all retries fail, the extraction halts and logs a failure event
3. Given a snapshot extraction completes successfully
   - When the results are reviewed
   - Then the snapshot contains all active PO lines from the ERP with no write-back to the ERP per NFR20
   - And the snapshot timestamp and record count are recorded for reporting
4. Given this is the first-ever ingestion run (no previous snapshot exists)
   - When the snapshot extraction runs in baseline mode per FR5
   - Then all extracted records are treated as new PO lines without change detection
   - And POLine records are created in the app database from the baseline snapshot
   - And an audit event is logged recording the baseline initialization

## Tasks / Subtasks

- [x] Task 1: Implement snapshot extractor service and data persistence (AC: 1, 3)
  - [x] Subtask 1.1: Implement extraction flow in `apps/ingestion/snapshot.py`
  - [x] Subtask 1.2: Persist extracted records as `ERPSnapshot` entries with run IDs
- [x] Task 2: Add resilient ERP read retry behavior (AC: 2)
  - [x] Subtask 2.1: Add configurable retry/backoff settings
  - [x] Subtask 2.2: Log/emit failure event on retry exhaustion
- [x] Task 3: Implement baseline mode initialization path (AC: 4)
  - [x] Subtask 3.1: Create `POLine` rows from baseline snapshot
  - [x] Subtask 3.2: Create baseline audit event
- [x] Task 4: Add tests and command-level validation (AC: 1-4)
  - [x] Subtask 4.1: Add extraction and retry unit tests
  - [x] Subtask 4.2: Add baseline-mode integration tests
  - [x] Subtask 4.3: Run tests and Django checks

## Dev Notes

- Reads against ERP must be strictly read-only and routed to `erp` database alias.
- Keep retry parameters configurable and surfaced for operations.
- Snapshot write path should be deterministic and idempotent per run identifier.

### Project Structure Notes

- Main service logic in `apps/ingestion/snapshot.py`.
- Supporting tests in `apps/ingestion/tests/`.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.2)
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/prd.md`

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- `.venv/bin/python manage.py test apps.ingestion.tests.test_snapshot --settings=po_tracking.settings.development -v 2`
- `.venv/bin/python manage.py test --settings=po_tracking.settings.development -v 1`
- `.venv/bin/python manage.py check --settings=po_tracking.settings.development`

### Completion Notes List

- Implemented `apps/ingestion/snapshot.py` with ERP snapshot extraction flow, active-line filtering, item/supplier mapping support, per-run persistence into `ERPSnapshot`, and run metadata return object.
- Added resilient retry/backoff behavior controlled by settings (`INGESTION_ERP_RETRY_COUNT`, `INGESTION_ERP_RETRY_BACKOFF_SECONDS`) and failure audit logging via `ingestion.snapshot.failed`.
- Implemented baseline initialization path that creates `POLine` records from the snapshot run and logs baseline audit events (`ingestion.baseline.initialized`).
- Added ingestion configuration defaults in settings and `.env.example`, including inactive ERP statuses and default supplier fallback values.
- Added focused tests for persistence, retry/recovery, retry exhaustion failure logging, and baseline initialization (`apps/ingestion/tests/test_snapshot.py`).
- Verified no regressions by running the full Django test suite (70 tests, all passing).

### File List

- `apps/ingestion/snapshot.py`
- `apps/ingestion/tests/test_snapshot.py`
- `apps/ingestion/erp_models.py`
- `po_tracking/settings/base.py`
- `.env.example`
- `_bmad-output/implementation-artifacts/2-2-erp-snapshot-extraction.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Senior Developer Review

**Reviewer:** Senior Dev Agent | **Date:** 2026-02-13 | **Outcome:** Approved after fixes

| ID | Severity | Location | Finding | Resolution |
|----|----------|----------|---------|------------|
| H1 | HIGH | `snapshot.py:_initialize_baseline_from_snapshot_run` | `POLine.bulk_create` and `create_audit_event` were not wrapped in `transaction.atomic()` — a crash between the two writes leaves DB in a partially-initialized state with no audit record. | Wrapped both operations in a single `transaction.atomic()` block. |
| H2 | HIGH | `tests/test_snapshot.py` | `_extract_active_erp_rows` had zero test coverage — all 4 service tests mocked it wholesale, leaving inactive-status filtering, xref mapping, and supplier assignment completely untested. | Added new `ExtractActiveERPRowsTests` class with 5 focused tests covering inactive-status exclusion, all configured statuses, xref SKU/item resolution, fallback supplier lazy-load, and no-fallback path. |
| M1 | MEDIUM | `snapshot.py:_extract_active_erp_rows` | `_get_default_supplier()` was called unconditionally before the loop — creating (or fetching) the DEFAULT supplier as a side effect even when every row has a valid xref, causing an unnecessary DB write. | Made `fallback_supplier` lazy: initialized to `None`, populated only on first xref-miss. |
| M2 | MEDIUM | `snapshot.py:run_snapshot_extraction` | Baseline auto-detection (`ERPSnapshot.objects.exists()`) ran outside the `transaction.atomic()` block — two concurrent first-ever runs could both see an empty table and both trigger baseline initialization. | Moved the auto-detection query inside the same `transaction.atomic()` block used for snapshot persistence (using `exclude(run_identifier=...)` to avoid counting the current run). |
| M3 | MEDIUM | `tests/test_snapshot.py` | No tests for `baseline_mode=None` auto-detection path (both the "first run triggers baseline" and "subsequent run skips baseline" branches). | Added `test_baseline_auto_triggered_when_no_prior_snapshots_exist` and `test_baseline_not_auto_triggered_when_prior_snapshots_exist`. |
| M4 | MEDIUM | `snapshot.py:_extract_with_retry` | Only caught `OperationalError` — other exceptions from ERP ODBC drivers (e.g. `InterfaceError`, `pyodbc.Error`) bypassed retry logic and failure logging entirely. | Changed to `except Exception as exc` to ensure all exceptions are retried and ultimately logged via the failure audit event. |
| L1 | LOW | `snapshot.py:_extract_with_retry` | `return []` at end of function was unreachable dead code — the loop either returns or raises on every path. | Replaced with `raise RuntimeError("retry_count must be >= 1")  # pragma: no cover` with a comment explaining it is protected by `max(..., 1)` above. |
| L2 | LOW | `snapshot.py:_extract_active_erp_rows` | `getattr(row, "current_status", "")` was vestigial — `current_status` is now a defined field on `ERPOrderLine`; `getattr` with default masks `AttributeError` that should never occur. | Changed to `row.current_status` direct field access (with `or ""` guard for null values). |

**Test results post-fix:** 11 tests, 0 failures (up from 4 tests pre-review).

## Change Log

- 2026-02-13: Implemented Story 2.2 snapshot extraction service, retry logic, baseline initialization, and test coverage; status moved to `review`.
- 2026-02-13: Senior developer review — applied fixes for H1 (atomic baseline), H2 (extraction test coverage), M1 (lazy supplier), M2 (baseline race condition), M3 (auto-detection tests), M4 (broad exception catching), L1 (dead code), L2 (direct field access); status moved to `done`.
