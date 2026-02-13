from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.po.models import Supplier


class UserModelTests(TestCase):
    def test_auth_user_model_setting_points_to_accounts_user(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")

    def test_user_role_choices_and_nullable_supplier_fk(self):
        user_model = get_user_model()
        role_field = user_model._meta.get_field("role")
        self.assertEqual(
            [choice[0] for choice in role_field.choices],
            ["admin", "planner", "expeditor"],
        )

        supplier_field = user_model._meta.get_field("supplier")
        self.assertTrue(supplier_field.null)
        self.assertEqual(supplier_field.related_model, Supplier)

    def test_session_policy_settings_contract(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 1800)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)


class SupplierModelTests(TestCase):
    def test_supplier_has_required_fields(self):
        meta = Supplier._meta
        name_field = meta.get_field("name")
        code_field = meta.get_field("code")
        self.assertEqual(name_field.max_length, 255)
        self.assertEqual(code_field.max_length, 64)
        self.assertTrue(code_field.unique)

    def test_supplier_str(self):
        supplier = Supplier(name="Acme Corp", code="ACME")
        self.assertEqual(str(supplier), "ACME - Acme Corp")

