"""
Password reset by emailed 6-digit code (or the link in the same email).

Flow
----
1. POST /api/accounts/password/reset/          {email}
   Always answers 200 with a generic message so account existence is never
   revealed. If an active account matches, a one-time code is emailed.
2. POST /api/accounts/password/reset/confirm/  {email, code, password}
   Checks the code, applies password validators, sets the new password and
   signs the user out everywhere (refresh tokens are blacklisted).

Codes are stored hashed, expire after PASSWORD_RESET_CODE_MINUTES, allow
PASSWORD_RESET_MAX_ATTEMPTS wrong guesses, and can only be used once.
"""
import logging
import secrets
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import PasswordResetCode

logger = logging.getLogger(__name__)
User = get_user_model()

CODE_MINUTES = getattr(settings, "PASSWORD_RESET_CODE_MINUTES", 15)
MAX_ATTEMPTS = getattr(settings, "PASSWORD_RESET_MAX_ATTEMPTS", 5)
RESEND_COOLDOWN_SECONDS = getattr(settings, "PASSWORD_RESET_RESEND_SECONDS", 60)

GENERIC_REQUEST_MESSAGE = (
    "If an active account uses that email address, we've sent a 6-digit reset code to it. "
    "The code expires in {minutes} minutes."
)
INVALID_CODE_MESSAGE = "That code is invalid or has expired. Request a new code and try again."


def _generate_code():
    return f"{secrets.randbelow(1_000_000):06d}"


def _find_user(email):
    return (
        User.objects.filter(email__iexact=email.strip(), is_active=True)
        .order_by("id")
        .first()
    )


def _build_email(user, code, email):
    frontend = (getattr(settings, "FRONTEND_URL", "") or "").rstrip("/")
    link = ""
    if frontend:
        link = f"{frontend}/reset-password?{urlencode({'email': email, 'code': code})}"
    name = user.get_full_name() or user.username

    text = (
        f"Hello {name},\n\n"
        f"Your Pseudosphere password reset code is: {code}\n\n"
        f"It expires in {CODE_MINUTES} minutes and can be used once.\n"
        + (f"Or open this link to continue: {link}\n\n" if link else "\n")
        + "If you didn't ask for this, you can ignore this email — your password won't change."
    )
    link_html = (
        f'<p style="margin:24px 0"><a href="{link}" style="background:#0f766e;color:#fff;'
        f'padding:12px 22px;border-radius:10px;text-decoration:none;font-weight:600">'
        f"Choose a new password</a></p>"
        if link
        else ""
    )
    html = f"""
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:480px;margin:auto;padding:24px;color:#0f172a">
  <h2 style="margin:0 0 8px;color:#0f766e">Pseudosphere</h2>
  <p>Hello {name},</p>
  <p>Use this code to reset your password:</p>
  <p style="font-size:34px;letter-spacing:8px;font-weight:700;margin:16px 0;color:#0f172a">{code}</p>
  <p style="color:#475569">It expires in {CODE_MINUTES} minutes and can be used once.</p>
  {link_html}
  <p style="color:#64748b;font-size:13px">If you didn't ask for this, ignore this email — your password won't change.</p>
</div>"""
    return text, html


def send_reset_code_email(user, code):
    """Send the code. Returns True on success; logs (never raises) on failure."""
    text, html = _build_email(user, code, user.email)
    message = EmailMultiAlternatives(
        subject="Your Pseudosphere password reset code",
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html, "text/html")
    try:
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception(
            "Password-reset email could not be delivered. Check EMAIL_HOST, EMAIL_HOST_USER, "
            "EMAIL_HOST_PASSWORD and DEFAULT_FROM_EMAIL (run `python manage.py send_test_email you@example.com`)."
        )
        return False


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        message = GENERIC_REQUEST_MESSAGE.format(minutes=CODE_MINUTES)
        if not email:
            return Response({"email": ["Enter your email address."]}, status=status.HTTP_400_BAD_REQUEST)

        user = _find_user(email)
        if user is None:
            logger.info("Password reset requested for an unknown or inactive email.")
            return Response({"detail": message})

        latest = PasswordResetCode.objects.filter(user=user).order_by("-created_at").first()
        if latest and latest.created_at > timezone.now() - timedelta(seconds=RESEND_COOLDOWN_SECONDS):
            # Inside the cooldown: stay generic, don't send another email.
            return Response({"detail": message})

        code = _generate_code()
        with transaction.atomic():
            PasswordResetCode.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
            PasswordResetCode.objects.create(
                user=user,
                code_hash=make_password(code),
                expires_at=timezone.now() + timedelta(minutes=CODE_MINUTES),
            )
        send_reset_code_email(user, code)
        return Response({"detail": message})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        code = str(request.data.get("code") or "").strip()
        password = request.data.get("password") or ""

        if not email or not code or not password:
            return Response(
                {"detail": "Email, code and new password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = _find_user(email)
        record = None
        if user:
            record = (
                PasswordResetCode.objects.filter(user=user, used_at__isnull=True)
                .order_by("-created_at")
                .first()
            )
        if record is None or record.expires_at < timezone.now() or record.attempts >= MAX_ATTEMPTS:
            return Response({"detail": INVALID_CODE_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(code, record.code_hash):
            record.attempts += 1
            record.save(update_fields=["attempts"])
            return Response({"detail": INVALID_CODE_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password, user)
        except DjangoValidationError as exc:
            return Response({"password": list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user.set_password(password)
            user.save(update_fields=["password"])
            PasswordResetCode.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
            _sign_out_everywhere(user)
        return Response({"detail": "Password updated. You can now sign in."})


def _sign_out_everywhere(user):
    """Blacklist every outstanding refresh token for the user."""
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)
