from datetime import date

from django.db import models

from accounts.models import TeacherProfile
from classes.models import ClassRoom
from subjects.models import Subject


# =====================================================
# CURRENT ACADEMIC YEAR
# =====================================================

def current_academic_year():
    year = date.today().year
    return f"{year}/{year + 1}"


# =====================================================
# TEACHER ASSIGNMENT
# =====================================================

class TeacherAssignment(models.Model):

    class Term(models.TextChoices):

        TERM_1 = "Term 1", "Term 1"
        TERM_2 = "Term 2", "Term 2"
        TERM_3 = "Term 3", "Term 3"

    # =================================================
    # TEACHER
    # =================================================

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    # =================================================
    # CLASSROOM
    # =================================================

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    # =================================================
    # SUBJECT
    # =================================================

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    # =================================================
    # ACADEMIC YEAR
    # =================================================

    academic_year = models.CharField(
        max_length=9,
        default=current_academic_year,
    )

    # =================================================
    # TERM
    # =================================================

    term = models.CharField(
        max_length=10,
        choices=Term.choices,
    )

    # =================================================
    # STATUS
    # =================================================

    is_active = models.BooleanField(
        default=True
    )

    # =================================================
    # CLASS TEACHER
    # =================================================

    is_class_teacher = models.BooleanField(
        default=False
    )

    # =================================================
    # DATES
    # =================================================

    assigned_date = models.DateField(
        auto_now_add=True
    )

    end_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =================================================
    # META
    # =================================================

    class Meta:

        ordering = [
            "academic_year",
            "term",
            "classroom",
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "teacher",
                    "classroom",
                    "subject",
                    "academic_year",
                    "term",
                ],
                name="unique_teacher_class_subject_term",
            ),

        ]

        indexes = [

            models.Index(
                fields=[
                    "teacher",
                    "academic_year",
                    "term",
                ]
            ),

            models.Index(
                fields=[
                    "classroom",
                    "academic_year",
                    "term",
                ]
            ),

            models.Index(
                fields=[
                    "subject",
                    "academic_year",
                    "term",
                ]
            ),

        ]

    # =================================================
    # STRING
    # =================================================

    def __str__(self):

        teacher_name = (
            self.teacher.user.get_full_name()
            if self.teacher and self.teacher.user
            else "Unknown Teacher"
        )

        return (
            f"{teacher_name} - "
            f"{self.subject.name} - "
            f"{self.classroom}"
        )

class ClassAssignment(models.Model):
    """Homework/classwork created by a teacher for one classroom."""
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="class_assignments", db_index=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="class_assignments")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="class_assignments")
    created_by = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT, related_name="class_assignments")
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    attachment = models.FileField(upload_to="assignments/", blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.classroom}"


class HomeworkSubmission(models.Model):
    """A student's submission for a published class assignment."""
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        LATE = "late", "Late"
        RETURNED = "returned", "Returned for revision"
        GRADED = "graded", "Graded"

    assignment = models.ForeignKey(ClassAssignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="homework_submissions")
    text_response = models.TextField(blank=True)
    attachment = models.FileField(upload_to="homework_submissions/%Y/%m/", blank=True, null=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SUBMITTED)
    grade = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    graded_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, blank=True, null=True, related_name="graded_homework_submissions")

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [models.UniqueConstraint(fields=["assignment", "student"], name="unique_homework_submission_per_student")]

    def __str__(self):
        return f"{self.assignment.title} - {self.student}"
