from django.db import models


class Subject(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.PROTECT, null=True, blank=True, related_name="subjects", db_index=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "name"], name="unique_school_subject_name"),
            models.UniqueConstraint(fields=["school", "code"], name="unique_school_subject_code"),
        ]

    def __str__(self):
        return self.name 