from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import CustomUser
from classes.models import ClassRoom
from schools.models import School
from subjects.models import Subject
from .models import ClassAssignment


class ClassAssignmentTenantTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.school_a = School.objects.create(name="School A", email="a@example.test", status=School.Status.APPROVED)
        self.school_b = School.objects.create(name="School B", email="b@example.test", status=School.Status.APPROVED)
        self.admin_a = CustomUser.objects.create_user(username="admin_a", email="admin-a@example.test", password="Strong-test-password-2026!", role=CustomUser.Role.SCHOOL_ADMIN, school=self.school_a)
        self.admin_b = CustomUser.objects.create_user(username="admin_b", email="admin-b@example.test", password="Strong-test-password-2026!", role=CustomUser.Role.SCHOOL_ADMIN, school=self.school_b)
        self.class_a = ClassRoom.objects.create(school=self.school_a, grade="Grade 1", stream="A", capacity=30)
        self.class_b = ClassRoom.objects.create(school=self.school_b, grade="Grade 1", stream="A", capacity=30)
        self.subject_a = Subject.objects.create(school=self.school_a, name="Mathematics", code="MATH")
        self.subject_b = Subject.objects.create(school=self.school_b, name="Mathematics", code="MATH")
        self.assignment_a = ClassAssignment.objects.create(school=self.school_a, classroom=self.class_a, subject=self.subject_a, created_by=self.admin_a, title="A work", instructions="Complete questions 1-5.")
        self.assignment_b = ClassAssignment.objects.create(school=self.school_b, classroom=self.class_b, subject=self.subject_b, created_by=self.admin_b, title="B work", instructions="Complete questions 6-10.")

    def test_school_admin_only_lists_own_assignments(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.get("/api/assignments/homework/")
        self.assertEqual(response.status_code, 200)
        rows = response.data if isinstance(response.data, list) else response.data.get("results", [])
        self.assertEqual([row["id"] for row in rows], [self.assignment_a.id])

    def test_school_admin_cannot_create_assignment_for_another_school(self):
        self.client.force_authenticate(self.admin_a)
        response = self.client.post("/api/assignments/homework/", {"classroom": self.class_b.id, "subject": self.subject_b.id, "title": "Cross-school", "instructions": "Must be blocked."}, format="json")
        self.assertEqual(response.status_code, 400)
