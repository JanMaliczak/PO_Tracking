from django.test import TestCase

from apps.ingestion.erp_models import ERPItemXref, ERPOrderLine
from apps.ingestion.models import ERPChangeEvent, ERPSnapshot, ItemXref
from apps.ingestion.router import DatabaseRouter


class IngestionModelContractTests(TestCase):
    def test_ingestion_models_are_managed_and_migrate_on_default_db(self):
        self.assertTrue(ERPSnapshot._meta.managed)
        self.assertTrue(ERPChangeEvent._meta.managed)
        self.assertTrue(ItemXref._meta.managed)

    def test_erp_models_are_unmanaged_and_router_marks_them_as_erp(self):
        router = DatabaseRouter()
        self.assertFalse(ERPOrderLine._meta.managed)
        self.assertFalse(ERPItemXref._meta.managed)
        self.assertTrue(getattr(ERPOrderLine, "erp_managed", False))
        self.assertEqual(router.db_for_read(ERPOrderLine), "erp")
        self.assertFalse(router.allow_migrate("default", "ingestion", model=ERPOrderLine))

    def test_erp_model_write_is_blocked_by_router(self):
        router = DatabaseRouter()
        with self.assertRaises(RuntimeError):
            router.db_for_write(ERPOrderLine)

    def test_item_xref_has_expected_fields(self):
        self.assertEqual(ItemXref._meta.get_field("erp_item_code").max_length, 128)
        self.assertEqual(ItemXref._meta.get_field("mapped_sku").max_length, 128)
        self.assertEqual(ItemXref._meta.get_field("mapped_item").max_length, 255)
        self.assertEqual(ItemXref._meta.get_field("is_active").get_internal_type(), "BooleanField")

    def test_snapshot_and_change_event_contract_fields(self):
        self.assertEqual(ERPSnapshot._meta.get_field("run_identifier").max_length, 64)
        self.assertEqual(ERPChangeEvent._meta.get_field("field_name").max_length, 128)
        self.assertEqual(ERPChangeEvent._meta.get_field("detected_at").get_internal_type(), "DateTimeField")
