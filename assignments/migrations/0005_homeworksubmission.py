# Generated for the Pseudosphere Academy homework submission feature.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("assignments", "0004_classassignment"),
        ("students", "0010_alter_student_assessment_number"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="HomeworkSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text_response", models.TextField(blank=True)),
                ("attachment", models.FileField(blank=True, null=True, upload_to="homework_submissions/%Y/%m/")),
                ("status", models.CharField(choices=[("submitted", "Submitted"), ("late", "Late"), ("returned", "Returned for revision"), ("graded", "Graded")], default="submitted", max_length=12)),
                ("grade", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("feedback", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("assignment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="assignments.classassignment")),
                ("graded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="graded_homework_submissions", to=settings.AUTH_USER_MODEL)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="homework_submissions", to="students.student")),
            ],
            options={"ordering": ["-submitted_at"]},
        ),
        migrations.AddConstraint(model_name="homeworksubmission", constraint=models.UniqueConstraint(fields=("assignment", "student"), name="unique_homework_submission_per_student")),
    ]
