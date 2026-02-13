from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="planner_user",
            password="StrongPassword123!",
            role="planner",
        )

    def test_login_page_renders_with_accessible_labels(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, '<label for="id_username" class="form-label">Username</label>', html=True)
        self.assertContains(response, '<label for="id_password" class="form-label">Password</label>', html=True)

    def test_valid_login_redirects_to_home_and_creates_session(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "planner_user", "password": "StrongPassword123!"},
        )
        self.assertRedirects(response, reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_invalid_login_shows_generic_error_message(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "planner_user", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")
        self.assertNotContains(response, "username does not exist")
        self.assertNotContains(response, "password is incorrect")

    def test_logout_invalidates_session_and_redirects_to_login(self):
        self.client.login(username="planner_user", password="StrongPassword123!")
        previous_session_key = self.client.session.session_key

        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(Session.objects.filter(session_key=previous_session_key).exists())

    def test_expired_session_redirects_to_login(self):
        self.client.login(username="planner_user", password="StrongPassword123!")
        session_key = self.client.session.session_key

        # Expire the session by backdating its expiry in the database
        stored = Session.objects.get(session_key=session_key)
        stored.expire_date = timezone.now() - timezone.timedelta(seconds=1)
        stored.save()

        response = self.client.get(reverse("home"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('home')}")

