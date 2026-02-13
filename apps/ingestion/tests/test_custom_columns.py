from datetime import date, datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.ingestion.custom_columns import ingest_custom_columns_from_snapshot
from apps.ingestion.models import ERPSnapshot
from apps.po.models import POLine, Supplier


class CustomColumnIngestionTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(code="SUP-A", name="Supplier A")
        self.snapshot_ts = timezone.make_aware(datetime(2026, 2, 13, 12, 0, 0))

    def _snapshot(self, *, run_identifier: str, po_number: str, line_number: int, **extra):
        defaults = {
            "run_identifier": run_identifier,
            "snapshot_timestamp": self.snapshot_ts,
            "po_number": po_number,
            "line_number": line_number,
            "sku": "SKU-1",
            "item": "Item A",
            "supplier": self.supplier,
            "ordered_quantity": Decimal("10.000"),
            "delivered_quantity": Decimal("1.000"),
            "remaining_quantity": Decimal("9.000"),
            "in_date": None,
            "promised_date": None,
            "current_status": "OPEN",
            "source_quality": POLine.SOURCE_QUALITY_ERP,
            "custom_column_sources": {},
        }
        defaults.update(extra)
        return ERPSnapshot.objects.create(**defaults)

    def _poline(self, *, po_number: str, line_number: int, **extra):
        defaults = {
            "po_number": po_number,
            "line_number": line_number,
            "sku": "SKU-1",
            "item": "Item A",
            "supplier": self.supplier,
            "ordered_quantity": Decimal("10.000"),
            "delivered_quantity": Decimal("1.000"),
            "remaining_quantity": Decimal("9.000"),
            "source_quality": POLine.SOURCE_QUALITY_ERP,
            "custom_column_sources": {},
        }
        defaults.update(extra)
        return POLine.objects.create(**defaults)

    def test_ingest_populates_erp_custom_fields_and_marks_source(self):
        self._snapshot(
            run_identifier="run-cc",
            po_number="PO-1",
            line_number=1,
            custom_date_1=date(2026, 2, 20),
            custom_text_1="ERP-TEXT",
            custom_decimal_1=Decimal("12.345"),
        )
        po_line = self._poline(po_number="PO-1", line_number=1)

        result = ingest_custom_columns_from_snapshot(run_identifier="run-cc")

        po_line.refresh_from_db()
        self.assertEqual(result.updated_po_lines_count, 1)
        self.assertEqual(po_line.custom_date_1, date(2026, 2, 20))
        self.assertEqual(po_line.custom_text_1, "ERP-TEXT")
        self.assertEqual(po_line.custom_decimal_1, Decimal("12.345"))
        self.assertEqual(po_line.custom_column_sources.get("custom_date_1"), "erp")
        self.assertEqual(po_line.custom_column_sources.get("custom_text_1"), "erp")
        self.assertEqual(po_line.custom_column_sources.get("custom_decimal_1"), "erp")

    def test_user_sourced_values_are_not_overwritten(self):
        self._snapshot(
            run_identifier="run-cc",
            po_number="PO-1",
            line_number=1,
            custom_text_1="ERP-NEW",
            custom_text_2="ERP-SET",
        )
        po_line = self._poline(
            po_number="PO-1",
            line_number=1,
            custom_text_1="USER-VALUE",
            custom_column_sources={"custom_text_1": "user"},
        )

        ingest_custom_columns_from_snapshot(run_identifier="run-cc")

        po_line.refresh_from_db()
        self.assertEqual(po_line.custom_text_1, "USER-VALUE")
        self.assertEqual(po_line.custom_column_sources.get("custom_text_1"), "user")
        self.assertEqual(po_line.custom_text_2, "ERP-SET")
        self.assertEqual(po_line.custom_column_sources.get("custom_text_2"), "erp")

    def test_custom_mapping_extracts_from_mapped_snapshot_field(self):
        self._snapshot(
            run_identifier="run-cc-map",
            po_number="PO-1",
            line_number=1,
            final_customer="Mapped Customer",
        )
        po_line = self._poline(po_number="PO-1", line_number=1)

        result = ingest_custom_columns_from_snapshot(
            run_identifier="run-cc-map",
            mapping={"custom_text_2": "final_customer"},
        )

        po_line.refresh_from_db()
        self.assertEqual(result.populated_fields_count, 1)
        self.assertEqual(po_line.custom_text_2, "Mapped Customer")
        self.assertEqual(po_line.custom_column_sources.get("custom_text_2"), "erp")
