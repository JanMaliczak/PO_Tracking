from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.po.models import Supplier


class RbacEndpointTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="Supplier One", code="SUP-1")
        self.user_model = get_user_model()
        self.admin_user = self.user_model.objects.create_user(
            username="admin_user",
            password="StrongPassword123!",
            role="admin",
        )
        self.planner_user = self.user_model.objects.create_user(
            username="planner_user",
            password="StrongPassword123!",
            role="planner",
        )
        self.expeditor_user = self.user_model.objects.create_user(
            username="expeditor_user",
            password="StrongPassword123!",
            role="expeditor",
            supplier=self.supplier,
        )

    def test_admin_endpoint_allows_admin(self):
        self.client.login(username="admin_user", password="StrongPassword123!")
        response = self.client.get(reverse("admin_portal:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_endpoint_forbids_non_admin(self):
        self.client.login(username="planner_user", password="StrongPassword123!")
        response = self.client.get(reverse("admin_portal:dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_expeditor_action_forbids_planner(self):
        self.client.login(username="planner_user", password="StrongPassword123!")
        response = self.client.post(reverse("po:milestone_update"))
        self.assertEqual(response.status_code, 403)

    def test_expeditor_action_allows_expeditor(self):
        self.client.login(username="expeditor_user", password="StrongPassword123!")
        response = self.client.post(reverse("po:milestone_update"))
        self.assertEqual(response.status_code, 200)

    def test_htmx_forbidden_endpoint_returns_trigger_header(self):
        self.client.login(username="planner_user", password="StrongPassword123!")
        response = self.client.post(
            reverse("po:milestone_update"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("HX-Trigger", response.headers)
        self.assertIn("Access denied", response.headers["HX-Trigger"])

    def test_admin_cannot_update_milestone(self):
        """AC 3: milestone recording is expeditor-only; admins are not permitted."""
        self.client.login(username="admin_user", password="StrongPassword123!")
        response = self.client.post(reverse("po:milestone_update"))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_access_to_protected_endpoint_redirects_to_login(self):
        """Unauthenticated users must be redirected to login, not shown 403."""
        response = self.client.get(reverse("admin_portal:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_unauthenticated_htmx_access_to_protected_endpoint_redirects(self):
        """Unauthenticated HTMX requests receive a login redirect (302), not 403.
        HTMX callers must handle the redirect at the application level."""
        response = self.client.get(
            reverse("admin_portal:dashboard"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_expeditor_direct_url_access_to_admin_portal_is_blocked(self):
        """AC 3: URL manipulation must not bypass role enforcement.
        An expeditor navigating directly to /admin-portal/ must receive 403."""
        self.client.login(username="expeditor_user", password="StrongPassword123!")
        response = self.client.get(reverse("admin_portal:dashboard"))
        self.assertEqual(response.status_code, 403)

