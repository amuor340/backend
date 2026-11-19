from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import School

User = get_user_model()


class SchoolRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def payload(self, suffix="one"):
        return {
            "school_name": f"Example School {suffix}",
            "school_email": f"school-{suffix}@example.test",
            "school_phone": "0700000000",
            "admin_first_name": "School",
            "admin_last_name": "Admin",
            "admin_email": f"admin-{suffix}@example.test",
            "admin_username": f"schooladmin_{suffix}",
            "admin_password": "A-strong-test-password-2026!",
        }

    def test_registration_creates_pending_school_and_inactive_admin(self):
        response = self.client.post("/api/schools/register/", self.payload(), format="json")
        self.assertEqual(response.status_code, 201)
        school = School.objects.get(email="school-one@example.test")
        admin = User.objects.get(username="schooladmin_one")
        self.assertEqual(school.status, School.Status.PENDING)
        self.assertFalse(admin.is_active)
        self.assertEqual(admin.school_id, school.id)

    def test_only_unscoped_platform_admin_can_approve_school(self):
        self.client.post("/api/schools/register/", self.payload(), format="json")
        school = School.objects.get(email="school-one@example.test")
        platform_admin = User.objects.create_superuser(username="platform-root", email="root@example.test", password="A-strong-test-password-2026!")
        self.client.force_authenticate(platform_admin)
        response = self.client.post(f"/api/schools/{school.id}/approve/", {}, format="json")
        self.assertEqual(response.status_code, 200)
        school.refresh_from_db()
        self.assertEqual(school.status, School.Status.APPROVED)
        self.assertTrue(User.objects.get(username="schooladmin_one").is_active)

    def test_school_admin_cannot_see_other_school_registrations(self):
        school_a = School.objects.create(name="School A", email="a@example.test", status=School.Status.APPROVED)
        school_b = School.objects.create(name="School B", email="b@example.test", status=School.Status.PENDING)
        admin = User.objects.create_user(username="school-a-admin", email="admin-a@example.test", password="A-strong-test-password-2026!", role="SCHOOL_ADMIN", school=school_a)
        self.client.force_authenticate(admin)
        response = self.client.get("/api/schools/")
        self.assertEqual(response.status_code, 403)
