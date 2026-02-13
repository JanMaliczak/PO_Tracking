# Story 2.5: Historical Batch Reconstruction & Custom Column Ingestion

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin,
I want historical batch deliveries reconstructed from ERP data and custom columns populated from ERP sources,
So that the application reflects the complete delivery history and extended data fields from day one.

## Acceptance Criteria

1. Given the ERP snapshot contains DeliveredQty and InDate records for PO lines
   - When the batch reconstruction logic in `apps/ingestion/batch_reconstruction.py` runs per FR4
   - Then historical `Batch` records are created in `apps/batches/models.py` from the ERP delivery data
   - And each batch record captures: PO line FK, delivered quantity, delivery date (InDate), and `source='ingestion'`
   - And batch records are linked to their parent PO lines with correct quantity allocation
2. Given historical batches are reconstructed
   - When the reconstruction processes a PO line with multiple delivery records
   - Then separate batch records are created for each distinct delivery event
   - And the cumulative delivered quantity across batches matches the ERP's total DeliveredQty for that PO line
3. Given the admin has configured custom columns with ERP SQL column mappings (via Epic 8, or seed data)
   - When the custom column ingestion in `apps/ingestion/custom_columns.py` runs per FR8b
   - Then up to 15 custom column values (5 date, 5 text, 5 decimal) are extracted from the mapped ERP SQL columns
   - And the corresponding `custom_date_N`, `custom_text_N`, or `custom_decimal_N` fields on the `POLine` record are populated
4. Given custom column values are ingested from the ERP
   - When the source tracking is updated per FR8c
   - Then the `custom_column_sources` field on the `POLine` records the data source as `'erp'` for each ERP-populated custom column
   - And existing user-entered custom column values (source `'user'`) are not overwritten by ERP ingestion

## Tasks / Subtasks

- [x] Task 1: Implement historical batch reconstruction (AC: 1, 2)
  - [x] Subtask 1.1: Build reconstruction flow in `apps/ingestion/batch_reconstruction.py`
  - [x] Subtask 1.2: Persist `Batch` rows with accurate PO linkage and allocation
- [x] Task 2: Implement ERP custom column ingestion (AC: 3)
  - [x] Subtask 2.1: Implement mapped extraction in `apps/ingestion/custom_columns.py`
  - [x] Subtask 2.2: Populate 15 physical custom column fields on `POLine`
- [x] Task 3: Enforce custom source-tracking precedence (AC: 4)
  - [x] Subtask 3.1: Update `custom_column_sources` for ERP-populated values
  - [x] Subtask 3.2: Protect user-sourced values from overwrite
- [x] Task 4: Add batch and custom column regression tests (AC: 1-4)
  - [x] Subtask 4.1: Add multi-delivery reconstruction tests
  - [x] Subtask 4.2: Add custom-source precedence tests
  - [x] Subtask 4.3: Run tests and Django checks

## Dev Notes

- Batch reconstruction is foundational for Epic 4 timeline and delivery progress views.
- Source tracking rules (`erp` vs `user`) must be strict to preserve manual updates.

### Project Structure Notes

- Batch logic in `apps/ingestion/batch_reconstruction.py`.
- Custom column ingestion in `apps/ingestion/custom_columns.py`.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.5)
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/prd.md`

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- `.venv/bin/python manage.py makemigrations batches ingestion --settings=po_tracking.settings.development`
- `.venv/bin/python manage.py test apps.batches.tests.test_models apps.ingestion.tests.test_batch_reconstruction apps.ingestion.tests.test_custom_columns --settings=po_tracking.settings.development -v 2`
- `.venv/bin/python manage.py test --settings=po_tracking.settings.development -v 1`
- `.venv/bin/python manage.py check --settings=po_tracking.settings.development`

### Completion Notes List

- Added `Batch` domain model in `apps/batches/models.py` with ingestion/manual source taxonomy, PO-line linkage, delivery quantity/date, run identifier, uniqueness guard per run, and delivery-date index.
- Implemented historical delivery reconstruction service in `apps/ingestion/batch_reconstruction.py` that computes delivered-quantity deltas between previous/current snapshots and persists one ingestion batch per positive delta with deterministic idempotence behavior.
- Implemented ERP custom column ingestion service in `apps/ingestion/custom_columns.py` to populate up to 15 physical custom fields on `POLine` from snapshot data via configurable field mapping.
- Enforced source precedence in custom column ingestion so fields marked as user-sourced in `POLine.custom_column_sources` are not overwritten by ERP ingestion, while ERP-populated fields are explicitly marked with source `'erp'`.
- Extended snapshot schema and extraction path for Story 2.5 needs: added `ERPSnapshot.in_date`, extracted ERP `in_date` plus custom column values from ERP rows, and kept xref private metadata non-persistent.
- Added focused regression tests for batch reconstruction, custom column ingestion precedence/mapping, and Batch model contract constraints.
- Verified all tests and system checks pass after implementation (97 tests passing, Django check clean).

### File List

- `apps/batches/models.py`
- `apps/batches/migrations/0001_initial.py`
- `apps/batches/tests/test_models.py`
- `apps/ingestion/batch_reconstruction.py`
- `apps/ingestion/custom_columns.py`
- `apps/ingestion/models.py`
- `apps/ingestion/erp_models.py`
- `apps/ingestion/snapshot.py`
- `apps/ingestion/migrations/0002_erpsnapshot_in_date.py`
- `apps/ingestion/tests/test_batch_reconstruction.py`
- `apps/ingestion/tests/test_custom_columns.py`
- `_bmad-output/implementation-artifacts/2-5-historical-batch-reconstruction-custom-column-ingestion.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Senior Developer Review

| # | Severity | Finding | Resolution |
|---|----------|---------|------------|
| H1 | High | `Batch.UniqueConstraint` included `source` in fields — a second manual batch (empty `run_identifier`) would violate uniqueness, blocking Epic 6 manual batch creation | Changed to conditional `UniqueConstraint(fields=["po_line","run_identifier"], condition=Q(source="ingestion"))` in `models.py` and updated `0001_initial.py` migration accordingly |
| M1 | Medium | `reconstruct_historical_batches` created missing `POLine` rows and `Batch` rows in separate operations — partial failure left orphaned POLines without batches | Wrapped both `bulk_create` calls in a single `transaction.atomic()` block |
| M2 | Medium | `ingest_custom_columns_from_snapshot` overwrote existing POLine values with `None` ERP values and still marked source as `'erp'` — silently wiped data and inflated metrics | Added `if incoming_value is None: continue` guard before field assignment |
| M3 | Medium | `reconstruct_historical_batches(previous_run_identifier=None)` auto-detection path and first-ever-run (no prior snapshots) path had no test coverage | Added `test_auto_detects_most_recent_previous_run_when_not_specified` and `test_first_ever_reconstruction_with_no_prior_snapshots_treats_full_delivery_as_delta` |
| M4 | Medium | Missing-POLine auto-creation path in batch reconstruction was untested | Added `test_reconstruction_auto_creates_missing_poline_and_links_batch` |
| L1 | Low | `ingest_custom_columns_from_snapshot` triggered `bulk_update` even when incoming ERP values were identical to existing POLine values — unnecessary DB writes | Added `if getattr(po_line, po_field) == incoming_value: continue` guard to skip unchanged values |

All findings resolved. Full test suite: 100/100 pass.

## Change Log

- 2026-02-13: Implemented Story 2.5 historical batch reconstruction and custom column ingestion services (including source precedence protection), added schema updates/migrations, and added comprehensive regression tests; status moved to `review`.
- 2026-02-13: Senior developer code review — fixed conditional UniqueConstraint (H1), atomic transaction boundary (M1), null-value guard in custom column ingestion (M2), added 3 missing tests for auto-detection and POLine auto-creation paths (M3, M4), added unchanged-value skip guard (L1); status moved to `done`.
