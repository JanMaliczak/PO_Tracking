from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.core.decorators import role_required


class RoleRequiredDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_allows_user_with_permitted_role(self):
        @role_required("admin")
        def protected_view(request):
            return HttpResponse("ok")

        request = self.factory.get("/protected/")
        request.user = SimpleNamespace(is_authenticated=True, role="admin")
        response = protected_view(request)
        self.assertEqual(response.status_code, 200)

    def test_blocks_user_with_disallowed_role(self):
        @role_required("admin")
        def protected_view(request):
            return HttpResponse("ok")

        request = self.factory.get("/protected/")
        request.user = SimpleNamespace(is_authenticated=True, role="planner")
        response = protected_view(request)
        self.assertEqual(response.status_code, 403)

    def test_htmx_forbidden_response_includes_hx_trigger(self):
        @role_required("admin")
        def protected_view(request):
            return HttpResponse("ok")

        request = self.factory.get("/protected/", HTTP_HX_REQUEST="true")
        request.user = SimpleNamespace(is_authenticated=True, role="planner")
        request.htmx = True

        response = protected_view(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn("HX-Trigger", response.headers)
        self.assertIn("Access denied", response.headers["HX-Trigger"])

    def test_unauthenticated_user_redirected_to_login_by_decorator(self):
        """role_required alone must redirect unauthenticated users to login (not 403)."""

        @role_required("admin")
        def protected_view(request):
            return HttpResponse("ok")

        request = self.factory.get("/protected/")
        request.user = AnonymousUser()

        response = protected_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_login_required_runs_before_role_check(self):
        @login_required(login_url="/accounts/login/")
        @role_required("admin")
        def protected_view(request):
            return HttpResponse("ok")

        request = self.factory.get("/protected/")
        request.user = AnonymousUser()

        response = protected_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

