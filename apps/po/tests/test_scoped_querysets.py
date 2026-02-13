from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase

from apps.core.querysets import ScopedManager, scope_queryset_for_user


class ScopedQueryContractTests(SimpleTestCase):
    def test_expeditor_scope_filters_by_supplier_id(self):
        queryset = Mock()
        queryset.filter.return_value = "FILTERED"
        user = SimpleNamespace(is_authenticated=True, role="expeditor", supplier_id=7)

        result = scope_queryset_for_user(queryset, user, supplier_field="supplier")

        self.assertEqual(result, "FILTERED")
        queryset.filter.assert_called_once_with(supplier_id=7)

    def test_expeditor_without_supplier_returns_none_queryset(self):
        queryset = Mock()
        queryset.none.return_value = "NONE"
        user = SimpleNamespace(is_authenticated=True, role="expeditor", supplier_id=None)

        result = scope_queryset_for_user(queryset, user, supplier_field="supplier")

        self.assertEqual(result, "NONE")
        queryset.none.assert_called_once()

    def test_planner_and_admin_get_unfiltered_queryset(self):
        queryset = Mock()

        planner = SimpleNamespace(is_authenticated=True, role="planner")
        admin = SimpleNamespace(is_authenticated=True, role="admin")

        self.assertIs(scope_queryset_for_user(queryset, planner), queryset)
        self.assertIs(scope_queryset_for_user(queryset, admin), queryset)
        queryset.filter.assert_not_called()
        queryset.none.assert_not_called()

    def test_scoped_manager_for_user_delegates_to_queryset_method(self):
        manager = ScopedManager()
        manager.supplier_field = "supplier"
        qs = Mock()
        qs.for_user.return_value = "SCOPED_QS"
        manager.get_queryset = Mock(return_value=qs)

        user = SimpleNamespace(is_authenticated=True, role="expeditor", supplier_id=1)
        result = manager.for_user(user)

        self.assertEqual(result, "SCOPED_QS")
        qs.for_user.assert_called_once_with(user, supplier_field="supplier")

