import unittest
from pathlib import Path


class TestStory11Scaffold(unittest.TestCase):
    def test_required_paths_exist(self):
        required = [
            Path("manage.py"),
            Path(".env.example"),
            Path("requirements/base.txt"),
            Path("requirements/development.txt"),
            Path("requirements/production.txt"),
            Path("po_tracking/settings/base.py"),
            Path("po_tracking/settings/development.py"),
            Path("po_tracking/settings/production.py"),
            Path("po_tracking/settings/production_eu.py"),
            Path("apps/ingestion/router.py"),
            Path("templates"),
            Path("static"),
        ]
        for path in required:
            self.assertTrue(path.exists(), f"Missing required path: {path}")

    def test_base_settings_contains_htmx_middleware_and_router(self):
        base_settings = Path("po_tracking/settings/base.py").read_text(encoding="utf-8")
        self.assertIn("django_htmx.middleware.HtmxMiddleware", base_settings)
        self.assertIn('DATABASE_ROUTERS = ["apps.ingestion.router.DatabaseRouter"]', base_settings)

    def test_requirements_pin_core_dependencies(self):
        req = Path("requirements/base.txt").read_text(encoding="utf-8")
        self.assertIn("Django==5.2.11", req)
        self.assertIn("mssql-django==1.6", req)
        self.assertIn("django-htmx==1.27.0", req)
        self.assertIn("django-environ==0.12.0", req)
        self.assertIn("waitress==3.0.2", req)
        self.assertIn("openpyxl==3.1.5", req)


if __name__ == "__main__":
    unittest.main()
