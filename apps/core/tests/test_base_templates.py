from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.test import SimpleTestCase, TestCase


class BaseTemplateStructureTests(SimpleTestCase):
    def _read_template(self, name):
        path = settings.BASE_DIR / "templates" / name
        self.assertTrue(path.exists(), f"templates/{name} must exist")
        return path.read_text(encoding="utf-8")

    def test_base_template_exists_and_contains_core_assets_and_layout(self):
        content = self._read_template("base.html")

        self.assertIn("bootstrap@5.3", content)
        self.assertIn("htmx.org@2.0", content)
        self.assertIn('hx-headers=\'{"X-CSRFToken": "{{ csrf_token }}"}\'', content)
        self.assertIn("{% block content %}", content)
        self.assertIn("navbar", content.lower())
        self.assertIn("PO Tracking", content)

    def test_base_auth_template_is_minimal_and_bootstrap_based(self):
        content = self._read_template("base_auth.html")

        self.assertIn("bootstrap@5.3", content)
        self.assertNotIn("navbar", content.lower())
        self.assertIn("{% block content %}", content)

    def test_reusable_partials_exist_and_render(self):
        partials = [
            "_partials/_toast.html",
            "_partials/_loading_spinner.html",
            "_partials/_confirm_modal.html",
        ]
        for name in partials:
            path = settings.BASE_DIR / "templates" / name
            self.assertTrue(path.exists(), f"Missing partial template: templates/{name}")

        for template_name in partials:
            rendered = get_template(template_name).render({})
            self.assertIsInstance(rendered, str)


class NavbarRenderingTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!", role="planner"
        )

    def test_authenticated_navbar_shows_username_role_and_logout(self):
        self.client.login(username="testuser", password="TestPass123!")
        response = self.client.get("/")
        content = response.content.decode()

        self.assertIn("testuser", content)
        self.assertIn("planner", content)
        self.assertContains(response, 'action="%s"' % "/accounts/logout/")
        self.assertContains(response, "Logout")
