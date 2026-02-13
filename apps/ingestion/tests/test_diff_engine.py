from __future__ import annotations

import time
from datetime import date, datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.ingestion.diff_engine import run_snapshot_diff
from apps.ingestion.models import ERPChangeEvent, ERPSnapshot
from apps.po.models import POLine, Supplier


class SnapshotDiffEngineTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(code="SUP-A", name="Supplier A")
        self.snapshot_ts = timezone.make_aware(datetime(2026, 2, 13, 12, 0, 0))

    def _snapshot(self, *, run_identifier: str, po_number: str, line_number: int, **overrides):
        values = {
            "run_identifier": run_identifier,
            "snapshot_timestamp": self.snapshot_ts,
            "po_number": po_number,
            "line_number": line_number,
            "sku": "SKU-1",
            "item": "Item 1",
            "supplier": self.supplier,
            "ordered_quantity": Decimal("10.000"),
            "delivered_quantity": Decimal("2.000"),
            "remaining_quantity": Decimal("8.000"),
            "promised_date": date(2026, 2, 20),
            "current_status": "OPEN",
            "po_insert_date": date(2026, 2, 1),
            "final_customer": "Customer A",
            "source_quality": POLine.SOURCE_QUALITY_ERP,
            "last_update_timestamp": self.snapshot_ts,
            "custom_column_sources": {},
        }
        values.update(overrides)
        return ERPSnapshot.objects.create(**values)

    def _poline(self, *, po_number: str, line_number: int, **overrides):
        values = {
            "po_number": po_number,
            "line_number": line_number,
            "sku": "SKU-1",
            "item": "Item 1",
            "supplier": self.supplier,
            "ordered_quantity": Decimal("10.000"),
            "delivered_quantity": Decimal("2.000"),
            "remaining_quantity": Decimal("8.000"),
            "promised_date": date(2026, 2, 20),
            "current_status": "OPEN",
            "po_insert_date": date(2026, 2, 1),
            "final_customer": "Customer A",
            "source_quality": POLine.SOURCE_QUALITY_ERP,
            "last_update_timestamp": self.snapshot_ts,
        }
        values.update(overrides)
        return POLine.objects.create(**values)

    def test_changed_line_generates_field_events_updates_poline_and_audit(self):
        self._snapshot(run_identifier="run-prev", po_number="PO-1", line_number=1)
        self._snapshot(
            run_identifier="run-cur",
            po_number="PO-1",
            line_number=1,
            ordered_quantity=Decimal("12.000"),
            current_status="IN_PRODUCTION",
        )
        po_line = self._poline(po_number="PO-1", line_number=1)

        result = run_snapshot_diff(current_run_identifier="run-cur", previous_run_identifier="run-prev")

        self.assertEqual(result.changed_po_lines_count, 1)
        self.assertEqual(result.new_po_lines_count, 0)
        self.assertEqual(result.change_events_count, 2)

        po_line.refresh_from_db()
        self.assertEqual(po_line.ordered_quantity, Decimal("12.000"))
        self.assertEqual(po_line.current_status, "IN_PRODUCTION")

        field_names = list(
            ERPChangeEvent.objects.filter(snapshot__run_identifier="run-cur", po_line=po_line)
            .order_by("field_name")
            .values_list("field_name", flat=True)
        )
        self.assertEqual(field_names, ["current_status", "ordered_quantity"])

        audit_event = AuditEvent.objects.get(event_type="ingestion.change", po_line=po_line)
        self.assertEqual(audit_event.source, AuditEvent.SOURCE_INGESTION)
        self.assertEqual(set(audit_event.previous_values.keys()), {"current_status", "ordered_quantity"})
        self.assertEqual(set(audit_event.new_values.keys()), {"current_status", "ordered_quantity"})

    def test_new_line_creates_poline_and_creation_audit_event(self):
        self._snapshot(run_identifier="run-prev", po_number="PO-1", line_number=1)
        self._snapshot(run_identifier="run-cur", po_number="PO-1", line_number=1)
        self._snapshot(run_identifier="run-cur", po_number="PO-2", line_number=2, sku="SKU-2", item="Item 2")

        result = run_snapshot_diff(current_run_identifier="run-cur", previous_run_identifier="run-prev")

        self.assertEqual(result.new_po_lines_count, 1)
        self.assertTrue(POLine.objects.filter(po_number="PO-2", line_number=2).exists())

        created_event = AuditEvent.objects.get(event_type="ingestion.po_line.created", po_line__po_number="PO-2", po_line__line_number=2)
        self.assertEqual(created_event.source, AuditEvent.SOURCE_INGESTION)

    def test_absent_line_is_not_deleted_and_is_marked_stale(self):
        self._snapshot(run_identifier="run-prev", po_number="PO-1", line_number=1)
        self._snapshot(run_identifier="run-prev", po_number="PO-2", line_number=2)
        self._snapshot(run_identifier="run-cur", po_number="PO-1", line_number=1)

        self._poline(po_number="PO-1", line_number=1)
        absent_line = self._poline(po_number="PO-2", line_number=2, is_stale=False, staleness_checked_at=None)

        result = run_snapshot_diff(current_run_identifier="run-cur", previous_run_identifier="run-prev")

        self.assertEqual(result.absent_po_lines_count, 1)
        self.assertIn(("PO-2", 2), result.absent_po_lines)

        absent_line.refresh_from_db()
        self.assertTrue(absent_line.is_stale)
        self.assertIsNotNone(absent_line.staleness_checked_at)
        self.assertTrue(POLine.objects.filter(po_number="PO-2", line_number=2).exists())

    def test_rerun_is_idempotent_for_same_current_run(self):
        self._snapshot(run_identifier="run-prev", po_number="PO-1", line_number=1)
        self._snapshot(
            run_identifier="run-cur",
            po_number="PO-1",
            line_number=1,
            ordered_quantity=Decimal("13.000"),
        )
        po_line = self._poline(po_number="PO-1", line_number=1)

        first = run_snapshot_diff(current_run_identifier="run-cur", previous_run_identifier="run-prev")
        second = run_snapshot_diff(current_run_identifier="run-cur", previous_run_identifier="run-prev")

        self.assertFalse(first.rerun_skipped)
        self.assertTrue(second.rerun_skipped)
        self.assertEqual(ERPChangeEvent.objects.filter(snapshot__run_identifier="run-cur", po_line=po_line).count(), 1)
        self.assertEqual(AuditEvent.objects.filter(event_type="ingestion.change", po_line=po_line).count(), 1)

    def test_performance_regression_5000_lines_executes_quickly(self):
        previous_snapshots = []
        current_snapshots = []
        polines = []
        for idx in range(1, 5001):
            po_number = f"PO-{idx:05d}"
            previous_snapshots.append(
                ERPSnapshot(
                    run_identifier="run-prev",
                    snapshot_timestamp=self.snapshot_ts,
                    po_number=po_number,
                    line_number=1,
                    sku="SKU",
                    item="Item",
                    supplier=self.supplier,
                    ordered_quantity=Decimal("10.000"),
                    delivered_quantity=Decimal("1.000"),
                    remaining_quantity=Decimal("9.000"),
                    promised_date=date(2026, 2, 20),
                    current_status="OPEN",
                    source_quality=POLine.SOURCE_QUALITY_ERP,
                    custom_column_sources={},
                )
            )
            current_snapshots.append(
                ERPSnapshot(
                    run_identifier="run-cur",
                    snapshot_timestamp=self.snapshot_ts,
                    po_number=po_number,
                    line_number=1,
                    sku="SKU",
                    item="Item",
                    supplier=self.supplier,
                    ordered_quantity=Decimal("10.000") if idx % 50 else Decimal("11.000"),
                    delivered_quantity=Decimal("1.000"),
                    remaining_quantity=Decimal("9.000"),
                    promised_date=date(2026, 2, 20),
                    current_status="OPEN",
                    source_quality=POLine.SOURCE_QUALITY_ERP,
                    custom_column_sources={},
                )
            )
            polines.append(
                POLine(
                    po_number=po_number,
                    line_number=1,
                    sku="SKU",
                    item="Item",
                    supplier=self.supplier,
                    ordered_quantity=Decimal("10.000"),
                    delivered_quantity=Decimal("1.000"),
                    remaining_quantity=Decimal("9.000"),
                    promised_date=date(2026, 2, 20),
                    current_status="OPEN",
                    source_quality=POLine.SOURCE_QUALITY_ERP,
                )
            )

        ERPSnapshot.objects.bulk_create(previous_snapshots, batch_size=1000)
        ERPSnapshot.objects.bulk_create(current_snapshots, batch_size=1000)
        POLine.objects.bulk_create(polines, batch_size=1000)

        started = time.perf_counter()
        result = run_snapshot_diff(current_run_identifier="run-cur", previous_run_identifier="run-prev")
        duration = time.perf_counter() - started

        self.assertEqual(result.processed_po_lines_count, 5000)
        self.assertEqual(result.changed_po_lines_count, 100)
        self.assertLess(duration, 25.0)

    def test_auto_detects_most_recent_previous_run_when_not_specified(self):
        """H2: previous_run_identifier=None auto-detects the most recent prior run."""
        earlier_ts = timezone.make_aware(datetime(2026, 2, 10, 8, 0, 0))
        later_ts = timezone.make_aware(datetime(2026, 2, 12, 8, 0, 0))

        self._snapshot(run_identifier="run-older", po_number="PO-1", line_number=1,
                       **{"snapshot_timestamp": earlier_ts})
        self._snapshot(run_identifier="run-latest", po_number="PO-1", line_number=1,
                       ordered_quantity=Decimal("11.000"), **{"snapshot_timestamp": later_ts})
        self._snapshot(run_identifier="run-cur", po_number="PO-1", line_number=1,
                       ordered_quantity=Decimal("12.000"))
        self._poline(po_number="PO-1", line_number=1, ordered_quantity=Decimal("11.000"))

        result = run_snapshot_diff(current_run_identifier="run-cur")  # no previous_run_identifier

        self.assertEqual(result.previous_run_identifier, "run-latest")
        self.assertEqual(result.changed_po_lines_count, 1)
        self.assertEqual(ERPChangeEvent.objects.filter(
            snapshot__run_identifier="run-cur", field_name="ordered_quantity"
        ).count(), 1)

    def test_first_ever_diff_with_no_prior_run_creates_all_lines_as_new(self):
        """H2: When no prior snapshots exist, all current lines are treated as new."""
        self._snapshot(run_identifier="run-first", po_number="PO-1", line_number=1)
        self._snapshot(run_identifier="run-first", po_number="PO-2", line_number=1, sku="SKU-2")

        result = run_snapshot_diff(current_run_identifier="run-first")  # no prior run

        self.assertIsNone(result.previous_run_identifier)
        self.assertEqual(result.new_po_lines_count, 2)
        self.assertEqual(result.changed_po_lines_count, 0)
        self.assertEqual(POLine.objects.count(), 2)
        self.assertEqual(
            AuditEvent.objects.filter(event_type="ingestion.po_line.created").count(), 2
        )
