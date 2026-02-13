from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from django.db import OperationalError
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.ingestion.models import ERPSnapshot
from apps.ingestion.snapshot import _extract_active_erp_rows, run_snapshot_extraction
from apps.po.models import POLine, Supplier


def _make_erp_row(**kwargs):
    """Return a minimal mock ERP order-line row."""
    defaults = dict(
        po_number="PO-ERP-1",
        line_number=1,
        sku="ERP-SKU",
        item_code="ERP-ITEM-1",
        ordered_quantity=Decimal("10"),
        delivered_quantity=Decimal("0"),
        remaining_quantity=Decimal("10"),
        promised_date=None,
        current_status="OPEN",
        po_insert_date=None,
        final_customer="",
        last_update_timestamp=None,
    )
    defaults.update(kwargs)
    return Mock(**defaults)


def _sample_record(*, supplier):
    return {
        "po_number": "PO-1001",
        "line_number": 10,
        "sku": "SKU-1",
        "item": "Item Family A",
        "supplier": supplier,
        "ordered_quantity": Decimal("10.000"),
        "delivered_quantity": Decimal("2.000"),
        "remaining_quantity": Decimal("8.000"),
        "promised_date": date(2026, 2, 15),
        "current_status": "OPEN",
        "po_insert_date": date(2026, 2, 1),
        "final_customer": "Customer A",
        "source_quality": "erp",
        "last_update_timestamp": timezone.make_aware(datetime(2026, 2, 13, 10, 0, 0)),
    }


class SnapshotExtractionServiceTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(code="SUP-A", name="Supplier A")

    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_snapshot_rows_are_persisted_for_run_identifier(self, extract_mock):
        extract_mock.return_value = [
            _sample_record(supplier=self.supplier),
            {**_sample_record(supplier=self.supplier), "po_number": "PO-1002", "line_number": 20},
        ]

        now = timezone.make_aware(datetime(2026, 2, 13, 11, 0, 0))
        result = run_snapshot_extraction(run_identifier="run-001", baseline_mode=False, now=now)

        self.assertEqual(result.run_identifier, "run-001")
        self.assertEqual(result.extracted_count, 2)
        self.assertEqual(result.snapshot_count, 2)
        self.assertFalse(result.baseline_initialized)
        self.assertEqual(ERPSnapshot.objects.filter(run_identifier="run-001").count(), 2)

    @override_settings(INGESTION_ERP_RETRY_COUNT=3, INGESTION_ERP_RETRY_BACKOFF_SECONDS=0.25)
    @patch("apps.ingestion.snapshot.time.sleep")
    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_retry_behavior_retries_before_success(self, extract_mock, sleep_mock):
        extract_mock.side_effect = [
            OperationalError("temporary ERP outage"),
            OperationalError("temporary ERP outage"),
            [_sample_record(supplier=self.supplier)],
        ]

        result = run_snapshot_extraction(run_identifier="run-retry", baseline_mode=False)

        self.assertEqual(result.snapshot_count, 1)
        self.assertEqual(extract_mock.call_count, 3)
        sleep_mock.assert_any_call(0.25)
        sleep_mock.assert_any_call(0.5)

    @override_settings(INGESTION_ERP_RETRY_COUNT=2, INGESTION_ERP_RETRY_BACKOFF_SECONDS=0.1)
    @patch("apps.ingestion.snapshot._extract_active_erp_rows", side_effect=OperationalError("erp unavailable"))
    def test_retry_exhaustion_logs_failure_event(self, _extract_mock):
        with self.assertRaises(OperationalError):
            run_snapshot_extraction(run_identifier="run-fail", baseline_mode=False)

        failure_event = AuditEvent.objects.get(event_type="ingestion.snapshot.failed")
        self.assertEqual(failure_event.source, AuditEvent.SOURCE_INGESTION)
        self.assertEqual(failure_event.new_values["attempts"], 2)

    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_baseline_mode_creates_po_lines_and_audit_event(self, extract_mock):
        extract_mock.return_value = [_sample_record(supplier=self.supplier)]

        result = run_snapshot_extraction(run_identifier="run-baseline", baseline_mode=True)

        self.assertTrue(result.baseline_initialized)
        self.assertEqual(result.baseline_created_po_lines, 1)
        self.assertEqual(POLine.objects.count(), 1)
        self.assertTrue(
            AuditEvent.objects.filter(
                event_type="ingestion.baseline.initialized",
                source=AuditEvent.SOURCE_INGESTION,
            ).exists()
        )

    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_baseline_auto_triggered_when_no_prior_snapshots_exist(self, extract_mock):
        """M3: baseline_mode=None (default) auto-triggers baseline on first-ever run."""
        extract_mock.return_value = [_sample_record(supplier=self.supplier)]

        result = run_snapshot_extraction(run_identifier="run-auto")  # baseline_mode defaults to None

        self.assertTrue(result.baseline_initialized)
        self.assertEqual(result.baseline_created_po_lines, 1)
        self.assertEqual(POLine.objects.count(), 1)

    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_baseline_not_auto_triggered_when_prior_snapshots_exist(self, extract_mock):
        """M3: baseline_mode=None must NOT trigger baseline when snapshots already exist."""
        extract_mock.return_value = [_sample_record(supplier=self.supplier)]
        # Seed a prior snapshot for a different run
        ERPSnapshot.objects.create(
            run_identifier="prior-run",
            snapshot_timestamp=timezone.now(),
            po_number="PO-OLD",
            line_number=1,
            sku="SKU-OLD",
            item="Item",
        )

        result = run_snapshot_extraction(run_identifier="run-second")  # baseline_mode defaults to None

        self.assertFalse(result.baseline_initialized)
        self.assertEqual(POLine.objects.count(), 0)


class ExtractActiveERPRowsTests(TestCase):
    """H2: direct tests for _extract_active_erp_rows logic (inactive filter + xref mapping)."""

    def setUp(self):
        self.supplier = Supplier.objects.create(code="SUP-A", name="Supplier A")

    @patch("apps.ingestion.snapshot.ERPOrderLine.objects")
    def test_inactive_status_rows_are_excluded(self, erp_objects_mock):
        active_row = _make_erp_row(po_number="PO-ACT", current_status="OPEN", item_code="ITEM-1")
        inactive_row = _make_erp_row(po_number="PO-CLOSED", current_status="closed", item_code="ITEM-2")
        erp_objects_mock.using.return_value.all.return_value = [active_row, inactive_row]

        with patch("apps.ingestion.snapshot._load_active_item_xrefs", return_value={}), \
             patch("apps.ingestion.snapshot._load_supplier_map", return_value={}), \
             patch("apps.ingestion.snapshot._get_default_supplier", return_value=self.supplier):
            records = _extract_active_erp_rows()

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["po_number"], "PO-ACT")

    @patch("apps.ingestion.snapshot.ERPOrderLine.objects")
    def test_all_configured_inactive_statuses_are_filtered(self, erp_objects_mock):
        rows = [_make_erp_row(po_number=f"PO-{s}", current_status=s, item_code="ITEM-X")
                for s in ("closed", "CANCELLED", "complete", "Completed")]
        erp_objects_mock.using.return_value.all.return_value = rows

        with patch("apps.ingestion.snapshot._load_active_item_xrefs", return_value={}), \
             patch("apps.ingestion.snapshot._load_supplier_map", return_value={}), \
             patch("apps.ingestion.snapshot._get_default_supplier", return_value=self.supplier):
            records = _extract_active_erp_rows()

        self.assertEqual(records, [])

    @patch("apps.ingestion.snapshot.ERPOrderLine.objects")
    def test_xref_mapping_resolves_sku_and_item(self, erp_objects_mock):
        row = _make_erp_row(item_code="ERP-ITEM-1", sku="ERP-RAW-SKU", current_status="OPEN")
        erp_objects_mock.using.return_value.all.return_value = [row]

        xref_map = {"ERP-ITEM-1": {"mapped_sku": "MAPPED-SKU", "mapped_item": "Product Family A", "supplier_code": "SUP-A"}}
        with patch("apps.ingestion.snapshot._load_active_item_xrefs", return_value=xref_map), \
             patch("apps.ingestion.snapshot._load_supplier_map", return_value={"SUP-A": self.supplier}):
            records = _extract_active_erp_rows()

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["sku"], "MAPPED-SKU")
        self.assertEqual(records[0]["item"], "Product Family A")
        self.assertEqual(records[0]["supplier"], self.supplier)
        self.assertFalse(records[0]["_xref_gap"])
        self.assertEqual(records[0]["_erp_item_code"], "ERP-ITEM-1")
        self.assertNotIn("xref_gap", records[0].get("custom_column_sources", {}))

    @patch("apps.ingestion.snapshot.ERPOrderLine.objects")
    def test_no_xref_uses_fallback_supplier_lazily(self, erp_objects_mock):
        """M1: _get_default_supplier() must be called only when no xref is found."""
        row = _make_erp_row(item_code="UNKNOWN-ITEM", current_status="OPEN")
        erp_objects_mock.using.return_value.all.return_value = [row]

        with patch("apps.ingestion.snapshot._load_active_item_xrefs", return_value={}), \
             patch("apps.ingestion.snapshot._load_supplier_map", return_value={}), \
             patch("apps.ingestion.snapshot._get_default_supplier", return_value=self.supplier) as fallback_mock:
            records = _extract_active_erp_rows()

        fallback_mock.assert_called_once()
        self.assertEqual(records[0]["supplier"], self.supplier)
        self.assertTrue(records[0]["_xref_gap"])
        self.assertEqual(records[0]["_erp_item_code"], "UNKNOWN-ITEM")
        self.assertNotIn("xref_gap", records[0].get("custom_column_sources", {}))

    @patch("apps.ingestion.snapshot.ERPOrderLine.objects")
    def test_xref_present_does_not_call_default_supplier(self, erp_objects_mock):
        """M1: _get_default_supplier() must NOT be called when every row has a valid xref."""
        row = _make_erp_row(item_code="ERP-ITEM-1", current_status="OPEN")
        erp_objects_mock.using.return_value.all.return_value = [row]

        xref_map = {"ERP-ITEM-1": {"mapped_sku": "SKU", "mapped_item": "Item", "supplier_code": "SUP-A"}}
        with patch("apps.ingestion.snapshot._load_active_item_xrefs", return_value=xref_map), \
             patch("apps.ingestion.snapshot._load_supplier_map", return_value={"SUP-A": self.supplier}), \
             patch("apps.ingestion.snapshot._get_default_supplier") as fallback_mock:
            _extract_active_erp_rows()

        fallback_mock.assert_not_called()


class XrefGapReportingTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(code="SUP-A", name="Supplier A")

    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_unmapped_codes_are_summarized_and_audited_per_unique_code(self, extract_mock):
        row = _sample_record(supplier=self.supplier)
        extract_mock.return_value = [
            {**row, "po_number": "PO-1", "line_number": 1, "_xref_gap": True, "_erp_item_code": "UNMAP-1"},
            {**row, "po_number": "PO-2", "line_number": 2, "_xref_gap": True, "_erp_item_code": "UNMAP-2"},
            {**row, "po_number": "PO-3", "line_number": 3, "_xref_gap": True, "_erp_item_code": "UNMAP-1"},
        ]

        before = timezone.now()
        result = run_snapshot_extraction(run_identifier="run-xref-gaps", baseline_mode=False)
        after = timezone.now()

        self.assertEqual(result.unmapped_item_count, 2)
        self.assertEqual(set(result.unmapped_item_codes), {"UNMAP-1", "UNMAP-2"})

        events = AuditEvent.objects.filter(event_type="xref_gap", source=AuditEvent.SOURCE_INGESTION).order_by("id")
        self.assertEqual(events.count(), 2)
        self.assertEqual(
            {event.new_values["erp_item_code"] for event in events},
            {"UNMAP-1", "UNMAP-2"},
        )
        for event in events:
            self.assertEqual(event.new_values["run_identifier"], "run-xref-gaps")
            self.assertGreaterEqual(event.timestamp, before)
            self.assertLessEqual(event.timestamp, after)

    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_no_unmapped_codes_yields_empty_summary_and_no_gap_events(self, extract_mock):
        row = _sample_record(supplier=self.supplier)
        extract_mock.return_value = [
            {**row, "po_number": "PO-1", "line_number": 1, "_xref_gap": False, "_erp_item_code": "ERP-ITEM-1"},
        ]

        result = run_snapshot_extraction(run_identifier="run-no-gaps", baseline_mode=False)

        self.assertEqual(result.unmapped_item_count, 0)
        self.assertEqual(result.unmapped_item_codes, ())
        self.assertFalse(AuditEvent.objects.filter(event_type="xref_gap").exists())

    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_baseline_poline_has_clean_custom_column_sources(self, extract_mock):
        """M2: xref gap private keys must not leak into POLine.custom_column_sources after baseline init."""
        row = _sample_record(supplier=self.supplier)
        extract_mock.return_value = [
            {**row, "po_number": "PO-GAP", "line_number": 1, "_xref_gap": True, "_erp_item_code": "UNMAP-X"},
        ]

        run_snapshot_extraction(run_identifier="run-baseline-clean", baseline_mode=True)

        po_line = POLine.objects.get(po_number="PO-GAP", line_number=1)
        self.assertNotIn("xref_gap", po_line.custom_column_sources)
        self.assertNotIn("erp_item_code", po_line.custom_column_sources)
        self.assertNotIn("_xref_gap", po_line.custom_column_sources)

    @patch("apps.ingestion.snapshot._extract_active_erp_rows")
    def test_gap_events_not_duplicated_on_rerun_with_same_run_identifier(self, extract_mock):
        """H2: idempotence guard — second call with same run_identifier emits no extra gap events."""
        row = _sample_record(supplier=self.supplier)
        extract_mock.return_value = [
            {**row, "po_number": "PO-1", "line_number": 1, "_xref_gap": True, "_erp_item_code": "UNMAP-X"},
        ]

        run_snapshot_extraction(run_identifier="run-idem", baseline_mode=False)
        run_snapshot_extraction(run_identifier="run-idem", baseline_mode=False)

        self.assertEqual(
            AuditEvent.objects.filter(event_type="xref_gap", new_values__run_identifier="run-idem").count(), 1
        )
