from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class AccountFlowTests(TestCase):
    def test_registration_creates_account_and_logs_user_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "Alex Student",
                "email": "alex@example.com",
                "role": Profile.Role.STUDENT,
                "password1": "Bright-River-47!",
                "password2": "Bright-River-47!",
            },
        )

        self.assertRedirects(response, reverse("accounts:dashboard"))
        user = get_user_model().objects.get(email="alex@example.com")
        self.assertTrue(user.check_password("Bright-River-47!"))
        self.assertEqual(user.profile.role, Profile.Role.STUDENT)
        self.assertIn("_auth_user_id", self.client.session)

    def test_registration_rejects_duplicate_email_without_case_sensitivity(self):
        get_user_model().objects.create_user(
            username="alex@example.com",
            email="alex@example.com",
            password="Bright-River-47!",
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "Another Alex",
                "email": "ALEX@EXAMPLE.COM",
                "role": Profile.Role.COMPANY,
                "password1": "Bright-River-47!",
                "password2": "Bright-River-47!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email already exists.")

    def test_login_uses_email_and_password(self):
        get_user_model().objects.create_user(
            username="alex@example.com",
            email="alex@example.com",
            password="Bright-River-47!",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"email": "alex@example.com", "password": "Bright-River-47!"},
        )

        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("accounts:dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}",
        )

    def test_dashboard_supports_admin_without_a_role_profile(self):
        admin = get_user_model().objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="Bright-River-47!",
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Administrator account")
