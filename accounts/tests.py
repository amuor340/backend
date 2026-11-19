from datetime import timedelta

from django.core import mail
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import CustomUser, PasswordResetCode

REQUEST_URL = "/api/accounts/password/reset/"
CONFIRM_URL = "/api/accounts/password/reset/confirm/"


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_URL="http://localhost:5173",
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {"password_reset": "1000/hour"},
    },
)
class PasswordResetCodeTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="amina", email="Amina@Example.com", password="OldPassw0rd!", role="TEACHER"
        )

    def _request_code(self, email="amina@example.com"):
        response = self.client.post(REQUEST_URL, {"email": email}, format="json")
        self.assertEqual(response.status_code, 200)
        return response

    def _last_code(self):
        body = mail.outbox[-1].body
        return next(part for part in body.split() if part.isdigit() and len(part) == 6)

    def test_sends_code_email_case_insensitive(self):
        self._request_code("AMINA@example.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["Amina@Example.com"])
        self.assertEqual(len(self._last_code()), 6)

    def test_unknown_email_is_generic_and_sends_nothing(self):
        response = self._request_code("nobody@example.com")
        self.assertIn("If an active account", response.data["detail"])
        self.assertEqual(len(mail.outbox), 0)

    def test_confirm_sets_password_once(self):
        self._request_code()
        code = self._last_code()
        ok = self.client.post(
            CONFIRM_URL, {"email": "amina@example.com", "code": code, "password": "NewStrongPass#2026"}, format="json"
        )
        self.assertEqual(ok.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass#2026"))
        again = self.client.post(
            CONFIRM_URL, {"email": "amina@example.com", "code": code, "password": "AnotherStrong#2026"}, format="json"
        )
        self.assertEqual(again.status_code, 400)

    def test_wrong_code_is_counted_and_locks_after_max_attempts(self):
        self._request_code()
        code = self._last_code()
        for _ in range(5):
            bad = self.client.post(
                CONFIRM_URL, {"email": "amina@example.com", "code": "000000", "password": "NewStrongPass#2026"}, format="json"
            )
            self.assertEqual(bad.status_code, 400)
        locked = self.client.post(
            CONFIRM_URL, {"email": "amina@example.com", "code": code, "password": "NewStrongPass#2026"}, format="json"
        )
        self.assertEqual(locked.status_code, 400)

    def test_expired_code_rejected(self):
        self._request_code()
        code = self._last_code()
        PasswordResetCode.objects.update(expires_at=timezone.now() - timedelta(minutes=1))
        response = self.client.post(
            CONFIRM_URL, {"email": "amina@example.com", "code": code, "password": "NewStrongPass#2026"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_weak_password_rejected_but_code_kept(self):
        self._request_code()
        code = self._last_code()
        weak = self.client.post(
            CONFIRM_URL, {"email": "amina@example.com", "code": code, "password": "12345678"}, format="json"
        )
        self.assertEqual(weak.status_code, 400)
        self.assertIn("password", weak.data)
