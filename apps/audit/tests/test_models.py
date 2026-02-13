from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.audit.models import AuditEvent
from apps.core.services import create_audit_event
from apps.po.models import POLine, Supplier


class AuditEventContractTests(TestCase):
    def setUp(self):
        supplier = Supplier.objects.create(name="Supplier One", code="SUP-1")
        self.user = get_user_model().objects.create_user(
            username="audit_user",
            password="StrongPassword123!",
            role="planner",
        )
        self.po_line = POLine.objects.create(
            po_number="PO-AUDIT",
            line_number=1,
            sku="SKU-AUDIT",
            item="CAT-AUDIT",
            supplier=supplier,
        )

    def test_create_audit_event_is_single_entrypoint_contract(self):
        event = create_audit_event(
            event_type="milestone_update",
            source=AuditEvent.SOURCE_MANUAL,
            po_line=self.po_line,
            user=self.user,
            previous_values={"status": "open"},
            new_values={"status": "closed"},
            reason="Manual correction",
        )

        self.assertEqual(event.event_type, "milestone_update")
        self.assertEqual(event.po_line_id, self.po_line.id)
        self.assertEqual(event.user_id, self.user.id)
        self.assertEqual(event.source, AuditEvent.SOURCE_MANUAL)
        self.assertEqual(event.previous_values, {"status": "open"})
        self.assertEqual(event.new_values, {"status": "closed"})
        self.assertEqual(event.reason, "Manual correction")

    def test_audit_event_append_only_contract_blocks_update_and_delete(self):
        event = create_audit_event(
            event_type="snapshot_ingested",
            source=AuditEvent.SOURCE_INGESTION,
            po_line=self.po_line,
        )

        with self.assertRaises(RuntimeError):
            AuditEvent.objects.filter(id=event.id).update(event_type="tampered")
        with self.assertRaises(RuntimeError):
            AuditEvent.objects.filter(id=event.id).delete()
        with self.assertRaises(RuntimeError):
            event.delete()

    def test_audit_event_save_on_existing_instance_is_blocked(self):
        """Verify that save() cannot be used to bypass the append-only contract."""
        event = create_audit_event(
            event_type="snapshot_ingested",
            source=AuditEvent.SOURCE_INGESTION,
            po_line=self.po_line,
        )

        event.event_type = "tampered"
        with self.assertRaises(RuntimeError):
            event.save()
