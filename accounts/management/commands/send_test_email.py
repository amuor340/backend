from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a test email to verify SMTP settings (used by password reset)."

    def add_arguments(self, parser):
        parser.add_argument("recipient")

    def handle(self, recipient, **options):
        self.stdout.write(f"Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Host:    {settings.EMAIL_HOST}:{settings.EMAIL_PORT} (user: {settings.EMAIL_HOST_USER or '-'})")
        try:
            sent = send_mail(
                "Pseudosphere test email",
                "If you can read this, outgoing email works.",
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
        except Exception as exc:
            raise CommandError(f"Sending failed: {exc}") from exc
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} message(s) to {recipient}."))
