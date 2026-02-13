import unittest

from apps.ingestion.router import DatabaseRouter


class _Meta:
    def __init__(self, app_label: str):
        self.app_label = app_label


class ERPModel:
    # erp_managed is a class-level attribute (not Meta) per ERPTableBase convention.
    erp_managed = True
    _meta = _Meta("ingestion")


class LocalModel:
    _meta = _Meta("po")


class TestDatabaseRouter(unittest.TestCase):
    def setUp(self):
        self.router = DatabaseRouter()

    def test_erp_reads_route_to_erp(self):
        self.assertEqual(self.router.db_for_read(ERPModel), "erp")

    def test_non_erp_reads_use_default_routing(self):
        self.assertIsNone(self.router.db_for_read(LocalModel))

    def test_erp_writes_are_blocked(self):
        with self.assertRaises(RuntimeError):
            self.router.db_for_write(ERPModel)

    def test_erp_migrations_are_blocked(self):
        self.assertFalse(self.router.allow_migrate("erp", "po"))
        self.assertFalse(self.router.allow_migrate("default", "ingestion", model=ERPModel))

    def test_non_erp_migrations_use_default_routing(self):
        self.assertIsNone(self.router.allow_migrate("default", "ingestion"))

    def test_erp_relations_are_blocked(self):
        left = ERPModel()
        right = LocalModel()
        self.assertFalse(self.router.allow_relation(left, right))

    def test_non_erp_relations_use_default_routing(self):
        left = LocalModel()
        right = LocalModel()
        self.assertIsNone(self.router.allow_relation(left, right))


if __name__ == "__main__":
    unittest.main()
