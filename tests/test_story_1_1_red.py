import importlib
import unittest
from pathlib import Path


class Story11ScaffoldRedTests(unittest.TestCase):
    def test_router_module_exists(self):
        # Red phase: this should fail before router implementation exists
        importlib.import_module("apps.ingestion.router")

    def test_manage_py_exists(self):
        self.assertTrue(Path("manage.py").exists(), "manage.py should exist at repo root")


if __name__ == "__main__":
    unittest.main()
