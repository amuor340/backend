from django.db import models
from django.core.exceptions import ValidationError

from schools.education import LEVEL_CHOICES, levels_for_systems


class ClassRoom(models.Model):
    # Every level of every supported curriculum (Kenya CBC, Kenya high school,
    # South Sudan primary and secondary). Which ones a school may use is controlled
    # by School.education_systems — see schools/education.py.
    GRADE_CHOICES = LEVEL_CHOICES

    STREAM_CHOICES = [(letter, letter) for letter in "ABCDEF"]

    school = models.ForeignKey("schools.School", on_delete=models.PROTECT, null=True, blank=True, related_name="classrooms", db_index=True)

    grade = models.CharField(
        max_length=20,
        choices=GRADE_CHOICES
    )

    stream = models.CharField(
        max_length=1,
        choices=STREAM_CHOICES
    )

    capacity = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0, editable=False)

    class_teacher = models.ForeignKey(
        "accounts.TeacherProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school", "grade", "stream"],
                name="unique_school_grade_stream",
            )
        ]
        ordering = ["grade", "stream"]

    def clean(self):
        """
        Prevent one teacher from being assigned
        to more than one classroom, and keep new classes inside the
        curricula the school teaches.
        """
        if self._state.adding and self.school_id and self.grade:
            allowed = levels_for_systems(self.school.education_systems)
            if self.grade not in allowed:
                raise ValidationError({
                    "grade": f"{self.grade} is not part of the education systems your school offers. "
                             "Add the curriculum under School settings first."
                })
        if self.class_teacher:
            teacher_school_id = self.class_teacher.user.school_id
            if self.school_id and teacher_school_id and self.school_id != teacher_school_id:
                raise ValidationError({"class_teacher": "The class teacher must belong to the same school."})
            exists = ClassRoom.objects.filter(
                class_teacher=self.class_teacher
            ).exclude(pk=self.pk).exists()

            if exists:
                raise ValidationError({
                    "class_teacher":
                    "This teacher is already assigned as a class teacher."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.grade} {self.stream}"