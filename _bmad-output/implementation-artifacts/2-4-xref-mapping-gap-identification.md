# Story 2.4: Xref Mapping & Gap Identification

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin,
I want PO lines mapped through the SKU cross-reference table with unmapped items flagged for review,
So that ERP item codes are correctly translated and data quality gaps are visible without failing the ingestion.

## Acceptance Criteria

1. Given the `ItemXref` table contains mappings from ERP item codes to application SKUs and Items
   - When the ingestion pipeline processes extracted PO line records
   - Then each record's ERP item code is looked up in the `ItemXref` table
   - And matched records have their `POLine.sku` and `POLine.item` fields populated from the cross-reference
2. Given a PO line's ERP item code is not found in the `ItemXref` table
   - When the xref lookup fails for that record per FR7
   - Then the PO line is still created/updated in the app database (ingestion does not fail) per NFR23
   - And the PO line is flagged as having an unmapped item code
   - And the unmapped item code is recorded in the ingestion results for admin review
3. Given the ingestion run completes
   - When xref gaps are summarized
   - Then a count of unmapped item codes is included in the ingestion results report
   - And an audit event with `event_type='xref_gap'` is logged for each unmapped item code within 60 seconds of detection per NFR29
   - And the list of unmapped codes is available for the admin monitoring dashboard (Epic 8)

## Tasks / Subtasks

- [x] Task 1: Implement xref mapping application in ingestion pipeline (AC: 1)
  - [x] Subtask 1.1: Resolve ERP item code against `ItemXref`
  - [x] Subtask 1.2: Populate `POLine.sku` and `POLine.item` for mapped rows
- [x] Task 2: Implement non-blocking gap handling (AC: 2)
  - [x] Subtask 2.1: Mark/flag unmapped lines without failing ingestion
  - [x] Subtask 2.2: Capture unmapped codes in run results
- [x] Task 3: Implement gap reporting and audit emission (AC: 3)
  - [x] Subtask 3.1: Add xref gap summary counts to ingestion report
  - [x] Subtask 3.2: Emit `xref_gap` audit events within time requirement
- [x] Task 4: Add tests for mapped/unmapped behaviors (AC: 1-3)
  - [x] Subtask 4.1: Add mapping behavior tests
  - [x] Subtask 4.2: Add reporting and audit timing tests
  - [x] Subtask 4.3: Run tests and Django checks

## Dev Notes

- Xref mapping must be best-effort and non-fatal for ingestion continuity.
- Keep unmapped-code outputs explicit for Epic 8 admin observability.

### Project Structure Notes

- Mapping logic in ingestion pipeline modules under `apps/ingestion/`.
- Tests under `apps/ingestion/tests/`.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.4)
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

- Extended `run_snapshot_extraction` in `apps/ingestion/snapshot.py` to summarize unmapped xref codes per run and return them in `SnapshotExtractionResult` as `unmapped_item_count` and `unmapped_item_codes`.
- Added explicit per-record xref flagging in extracted snapshot payloads via `custom_column_sources` (`xref_gap` + `erp_item_code`), while keeping ingestion non-fatal for unmapped codes.
- Added audit emission for xref gaps (`event_type='xref_gap'`, `source='ingestion'`) with one event per unique unmapped ERP item code per run.
- Kept mapped/unmapped behavior best-effort and deterministic: mapped rows still populate mapped SKU/item; unmapped rows still persist and are surfaced for admin review.
- Added and extended tests in `apps/ingestion/tests/test_snapshot.py` for xref gap flags on extracted rows, run summary counts, unique-code audit emission, and no-gap behavior.
- Verified the full suite and Django checks pass after changes (86 tests passing).

### File List

- `apps/ingestion/snapshot.py`
- `apps/ingestion/tests/test_snapshot.py`
- `_bmad-output/implementation-artifacts/2-4-xref-mapping-gap-identification.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Senior Developer Review

**Reviewer:** Senior Dev Agent | **Date:** 2026-02-13 | **Outcome:** Approved after fixes

| ID | Severity | Location | Finding | Resolution |
|----|----------|----------|---------|------------|
| H1 | HIGH | `snapshot.py:139–142` | `custom_column_sources` misused as internal ingestion metadata carrier — storing `{xref_gap, erp_item_code}` in a field intended for user-configurable custom column provenance (Epic 5). Caused: (1) spurious diff engine `ERPChangeEvent` entries when xref mapping status changes between runs, (2) internal flags leaking into user-facing `POLine.custom_column_sources` via baseline init, (3) architectural coupling between ingestion and the custom column system. | Changed to private in-memory keys `_xref_gap` / `_erp_item_code` in extracted records. Added stripping of underscore-prefixed keys before snapshot DB persistence. `custom_column_sources` remains clean for its intended purpose. |
| H2 | HIGH | `snapshot.py:263–273` | `_record_xref_gap_events` had no idempotence guard — calling `run_snapshot_extraction` twice with the same `run_identifier` (e.g. on partial failure retry) would emit duplicate `xref_gap` audit events. Snapshot persistence used `ignore_conflicts=True` (idempotent) but gap events were unguarded. | Added early-return check: if any `xref_gap` event for `run_identifier` already exists, skip emission. Added test `test_gap_events_not_duplicated_on_rerun_with_same_run_identifier`. |
| M1 | MEDIUM | `snapshot.py:263–273` | Gap event emission was not in a transaction — a failure midway through multiple `create_audit_event` calls would commit some gap events and lose others, with no rollback. | Wrapped the emission loop in `transaction.atomic()` so all gap events for a run are committed atomically. |
| M2 | MEDIUM | `test_snapshot.py` | No test verified that xref gap private keys do not leak into `POLine.custom_column_sources` after baseline initialization. | Added `test_baseline_poline_has_clean_custom_column_sources` asserting all xref gap metadata is absent from `POLine.custom_column_sources`. |
| L1 | LOW | `snapshot.py:266` | `xref_gap` event type uses underscore, inconsistent with project's dotted naming convention — but explicitly mandated by AC3. | Noted as AC-mandated; not changed. |
| L2 | LOW | `test_snapshot.py:272` | Timing assertion only verified events are within call duration, not the 60-second NFR29 boundary. | Noted; synchronous emission guarantees compliance far below 60s. |

**Test results post-fix:** 15 tests, 0 failures (up from 13 pre-review). Full suite: 88/88.

## Change Log

- 2026-02-13: Implemented Story 2.4 xref gap identification and reporting (non-blocking unmapped handling, run summary counts/lists, per-code `xref_gap` audit events, and test coverage); status moved to `review`.
- 2026-02-13: Senior developer review — applied fixes for H1 (private in-memory keys, clean custom_column_sources), H2 (idempotence guard for gap events), M1 (atomic gap event emission), M2 (POLine clean-source test); status moved to `done`.
