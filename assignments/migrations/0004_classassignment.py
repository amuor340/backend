import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("assignments", "0003_alter_teacherassignment_unique_together_and_more"),
        ("schools", "0001_initial"),
        ("classes", "0005_classroom_school_tenant_constraint"),
        ("subjects", "0002_subject_school_scoped_uniqueness"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="ClassAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("instructions", models.TextField()),
                ("attachment", models.FileField(blank=True, null=True, upload_to="assignments/")),
                ("due_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("classroom", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="class_assignments", to="classes.classroom")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="class_assignments", to=settings.AUTH_USER_MODEL)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="class_assignments", to="schools.school")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="class_assignments", to="subjects.subject")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
