from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.po.models import POLine, Supplier


class POLineModelContractTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="Supplier One", code="SUP-1")
        self.user_model = get_user_model()
        self.admin_user = self.user_model.objects.create_user(
            username="admin_poline",
            password="StrongPassword123!",
            role="admin",
        )
        self.expeditor_user = self.user_model.objects.create_user(
            username="expeditor_poline",
            password="StrongPassword123!",
            role="expeditor",
            supplier=self.supplier,
        )
        self.other_supplier = Supplier.objects.create(name="Supplier Two", code="SUP-2")

    def test_poline_fields_and_custom_columns_exist(self):
        meta = POLine._meta
        self.assertEqual(meta.get_field("po_number").max_length, 64)
        self.assertEqual(meta.get_field("line_number").get_internal_type(), "PositiveIntegerField")
        self.assertEqual(meta.get_field("custom_date_1").get_internal_type(), "DateField")
        self.assertEqual(meta.get_field("custom_text_1").max_length, 255)
        self.assertEqual(meta.get_field("custom_decimal_1").get_internal_type(), "DecimalField")
        self.assertEqual(meta.get_field("custom_column_sources").get_internal_type(), "JSONField")

    def test_for_user_manager_contract_scopes_expeditor_and_allows_admin(self):
        own_line = POLine.objects.create(
            po_number="PO-1",
            line_number=1,
            sku="SKU-1",
            item="CAT-1",
            supplier=self.supplier,
            custom_column_sources={"custom_text_1": "erp"},
        )
        other_line = POLine.objects.create(
            po_number="PO-2",
            line_number=1,
            sku="SKU-2",
            item="CAT-2",
            supplier=self.other_supplier,
            custom_column_sources={"custom_text_1": "erp"},
        )

        admin_ids = set(POLine.objects.for_user(self.admin_user).values_list("id", flat=True))
        expeditor_ids = set(POLine.objects.for_user(self.expeditor_user).values_list("id", flat=True))

        self.assertEqual(admin_ids, {own_line.id, other_line.id})
        self.assertEqual(expeditor_ids, {own_line.id})
