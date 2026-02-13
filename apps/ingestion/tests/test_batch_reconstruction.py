from datetime import date, datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.batches.models import Batch
from apps.ingestion.batch_reconstruction import reconstruct_historical_batches
from apps.ingestion.models import ERPSnapshot
from apps.po.models import POLine, Supplier


class BatchReconstructionTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(code="SUP-A", name="Supplier A")
        self.now = timezone.make_aware(datetime(2026, 2, 13, 12, 0, 0))

    def _snapshot(self, *, run_identifier: str, po_number: str, line_number: int, delivered: Decimal, in_date=None, **extra):
        defaults = {
            "run_identifier": run_identifier,
            "snapshot_timestamp": self.now,
            "po_number": po_number,
            "line_number": line_number,
            "sku": "SKU-1",
            "item": "Item A",
            "supplier": self.supplier,
            "ordered_quantity": Decimal("10.000"),
            "delivered_quantity": delivered,
            "remaining_quantity": Decimal("10.000") - delivered,
            "promised_date": date(2026, 2, 20),
            "current_status": "OPEN",
            "source_quality": POLine.SOURCE_QUALITY_ERP,
            "last_update_timestamp": self.now,
            "in_date": in_date,
            "custom_column_sources": {},
        }
        defaults.update(extra)
        return ERPSnapshot.objects.create(**defaults)

    def _poline(self, *, po_number: str, line_number: int):
        return POLine.objects.create(
            po_number=po_number,
            line_number=line_number,
            sku="SKU-1",
            item="Item A",
            supplier=self.supplier,
            ordered_quantity=Decimal("10.000"),
            delivered_quantity=Decimal("0"),
            remaining_quantity=Decimal("10.000"),
            source_quality=POLine.SOURCE_QUALITY_ERP,
        )

    def test_reconstruction_creates_ingestion_batch_for_positive_delta(self):
        self._snapshot(run_identifier="run-1", po_number="PO-1", line_number=1, delivered=Decimal("2.000"))
        self._snapshot(
            run_identifier="run-2",
            po_number="PO-1",
            line_number=1,
            delivered=Decimal("6.000"),
            in_date=date(2026, 2, 14),
        )
        po_line = self._poline(po_number="PO-1", line_number=1)

        result = reconstruct_historical_batches(current_run_identifier="run-2", previous_run_identifier="run-1")

        self.assertEqual(result.created_batches_count, 1)
        batch = Batch.objects.get(po_line=po_line, run_identifier="run-2")
        self.assertEqual(batch.source, Batch.SOURCE_INGESTION)
        self.assertEqual(batch.delivered_quantity, Decimal("4.000"))
        self.assertEqual(batch.delivery_date, date(2026, 2, 14))

    def test_multi_delivery_across_runs_creates_separate_batches_and_cumulative_matches_latest(self):
        self._snapshot(run_identifier="run-1", po_number="PO-1", line_number=1, delivered=Decimal("0.000"))
        self._snapshot(run_identifier="run-2", po_number="PO-1", line_number=1, delivered=Decimal("3.000"), in_date=date(2026, 2, 14))
        self._snapshot(run_identifier="run-3", po_number="PO-1", line_number=1, delivered=Decimal("7.000"), in_date=date(2026, 2, 15))
        po_line = self._poline(po_number="PO-1", line_number=1)

        reconstruct_historical_batches(current_run_identifier="run-2", previous_run_identifier="run-1")
        reconstruct_historical_batches(current_run_identifier="run-3", previous_run_identifier="run-2")

        batches = Batch.objects.filter(po_line=po_line, source=Batch.SOURCE_INGESTION).order_by("run_identifier")
        self.assertEqual(batches.count(), 2)
        self.assertEqual([batch.delivered_quantity for batch in batches], [Decimal("3.000"), Decimal("4.000")])
        self.assertEqual(sum(batch.delivered_quantity for batch in batches), Decimal("7.000"))

    def test_no_positive_delta_creates_no_batches(self):
        self._snapshot(run_identifier="run-1", po_number="PO-1", line_number=1, delivered=Decimal("6.000"))
        self._snapshot(run_identifier="run-2", po_number="PO-1", line_number=1, delivered=Decimal("6.000"))
        self._poline(po_number="PO-1", line_number=1)

        result = reconstruct_historical_batches(current_run_identifier="run-2", previous_run_identifier="run-1")

        self.assertEqual(result.created_batches_count, 0)
        self.assertFalse(Batch.objects.exists())

    def test_rerun_same_run_is_idempotent(self):
        self._snapshot(run_identifier="run-1", po_number="PO-1", line_number=1, delivered=Decimal("1.000"))
        self._snapshot(run_identifier="run-2", po_number="PO-1", line_number=1, delivered=Decimal("2.000"))
        self._poline(po_number="PO-1", line_number=1)

        first = reconstruct_historical_batches(current_run_identifier="run-2", previous_run_identifier="run-1")
        second = reconstruct_historical_batches(current_run_identifier="run-2", previous_run_identifier="run-1")

        self.assertEqual(first.created_batches_count, 1)
        self.assertEqual(second.created_batches_count, 0)
        self.assertEqual(Batch.objects.count(), 1)

    def test_auto_detects_most_recent_previous_run_when_not_specified(self):
        """M3: previous_run_identifier=None auto-detects the most recent prior snapshot run."""
        earlier_ts = timezone.make_aware(datetime(2026, 2, 10, 8, 0, 0))
        self._snapshot(run_identifier="run-old", po_number="PO-1", line_number=1,
                       delivered=Decimal("1.000"), **{"snapshot_timestamp": earlier_ts})
        self._snapshot(run_identifier="run-latest", po_number="PO-1", line_number=1,
                       delivered=Decimal("3.000"))
        self._snapshot(run_identifier="run-cur", po_number="PO-1", line_number=1,
                       delivered=Decimal("5.000"), in_date=date(2026, 2, 14))
        po_line = self._poline(po_number="PO-1", line_number=1)

        result = reconstruct_historical_batches(current_run_identifier="run-cur")

        self.assertEqual(result.created_batches_count, 1)
        batch = Batch.objects.get(po_line=po_line, run_identifier="run-cur")
        self.assertEqual(batch.delivered_quantity, Decimal("2.000"))  # 5.000 - 3.000

    def test_first_ever_reconstruction_with_no_prior_snapshots_treats_full_delivery_as_delta(self):
        """M3: when no prior snapshot exists, delta is computed from 0 → creates batch for full delivered qty."""
        self._snapshot(run_identifier="run-first", po_number="PO-1", line_number=1,
                       delivered=Decimal("4.000"), in_date=date(2026, 2, 14))
        po_line = self._poline(po_number="PO-1", line_number=1)

        result = reconstruct_historical_batches(current_run_identifier="run-first")

        self.assertEqual(result.run_identifier, "run-first")
        self.assertEqual(result.created_batches_count, 1)
        batch = Batch.objects.get(po_line=po_line, run_identifier="run-first")
        self.assertEqual(batch.delivered_quantity, Decimal("4.000"))

    def test_reconstruction_auto_creates_missing_poline_and_links_batch(self):
        """M4: if POLine does not exist, reconstruction creates it from snapshot data before batch linkage."""
        self._snapshot(run_identifier="run-prev", po_number="PO-NEW", line_number=1, delivered=Decimal("0.000"))
        self._snapshot(run_identifier="run-cur", po_number="PO-NEW", line_number=1,
                       delivered=Decimal("3.000"), in_date=date(2026, 2, 15))
        # Deliberately do NOT create a POLine

        result = reconstruct_historical_batches(current_run_identifier="run-cur", previous_run_identifier="run-prev")

        self.assertEqual(result.created_batches_count, 1)
        po_line = POLine.objects.get(po_number="PO-NEW", line_number=1)
        batch = Batch.objects.get(run_identifier="run-cur", po_line=po_line)
        self.assertEqual(batch.delivered_quantity, Decimal("3.000"))
        self.assertEqual(batch.delivery_date, date(2026, 2, 15))
