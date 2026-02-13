from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from apps.batches.models import Batch
from apps.po.models import POLine, Supplier


class BatchModelContractTests(TestCase):
    def test_batch_contract_fields(self):
        self.assertEqual(Batch._meta.get_field("source").max_length, 16)
        self.assertEqual(Batch._meta.get_field("delivered_quantity").get_internal_type(), "DecimalField")
        self.assertEqual(Batch._meta.get_field("delivery_date").get_internal_type(), "DateField")

    def test_unique_constraint_on_poline_run_source(self):
        supplier = Supplier.objects.create(code="SUP-A", name="Supplier A")
        po_line = POLine.objects.create(
            po_number="PO-1",
            line_number=1,
            sku="SKU-1",
            item="Item A",
            supplier=supplier,
            ordered_quantity=Decimal("10.000"),
            delivered_quantity=Decimal("0.000"),
            remaining_quantity=Decimal("10.000"),
        )
        Batch.objects.create(
            po_line=po_line,
            delivered_quantity=Decimal("2.000"),
            delivery_date="2026-02-14",
            source=Batch.SOURCE_INGESTION,
            run_identifier="run-1",
        )

        with self.assertRaises(IntegrityError):
            Batch.objects.create(
                po_line=po_line,
                delivered_quantity=Decimal("3.000"),
                delivery_date="2026-02-15",
                source=Batch.SOURCE_INGESTION,
                run_identifier="run-1",
            )
