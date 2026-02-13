import importlib
import os
import sys
import unittest


class TestSettingsImports(unittest.TestCase):
    def test_base_settings_import_and_contract(self):
        module = importlib.import_module("po_tracking.settings.base")
        self.assertIn("default", module.DATABASES)
        self.assertIn("erp", module.DATABASES)
        self.assertIn("apps.ingestion.router.DatabaseRouter", module.DATABASE_ROUTERS)
        self.assertIn("django_htmx.middleware.HtmxMiddleware", module.MIDDLEWARE)

    def test_development_settings_import_and_debug(self):
        module = importlib.import_module("po_tracking.settings.development")
        self.assertTrue(module.DEBUG)
        self.assertIn("default", module.DATABASES)
        self.assertIn("erp", module.DATABASES)

    def _reload_settings_module(self, module_name):
        """Clear cached settings modules and re-import fresh to avoid shared state bleed."""
        full_name = f"po_tracking.settings.{module_name}"
        # Remove child and base so DATABASES dict is reconstructed
        for mod in [full_name, "po_tracking.settings.base"]:
            sys.modules.pop(mod, None)
        return importlib.import_module(full_name)

    def test_production_settings_import(self):
        # Production settings require SECRET_KEY and ALLOWED_HOSTS — set them for test
        os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key-for-ci")
        os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver")
        module = self._reload_settings_module("production")
        self.assertFalse(module.DEBUG)
        self.assertIn("default", module.DATABASES)
        self.assertIn("erp", module.DATABASES)

    def test_production_eu_settings_import_and_erp_disabled(self):
        # Production EU settings require SECRET_KEY and ALLOWED_HOSTS — set them for test
        os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key-for-ci")
        os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver")
        module = self._reload_settings_module("production_eu")
        self.assertFalse(module.DEBUG)
        self.assertTrue(module.APP_DB_READ_ONLY)
        self.assertNotIn("erp", module.DATABASES)


if __name__ == "__main__":
    unittest.main()
