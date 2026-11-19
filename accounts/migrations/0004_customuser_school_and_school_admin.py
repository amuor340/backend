import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_studentprofile_parent_phone"), ("schools", "0001_initial")]
    operations = [
        migrations.AddField(model_name="customuser", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="users", to="schools.school")),
        migrations.AlterField(model_name="customuser", name="role", field=models.CharField(choices=[("SUPER_ADMIN", "Platform Super Admin"), ("SCHOOL_ADMIN", "School Administrator"), ("ACADEMIC_COORDINATOR", "Academic Coordinator"), ("ACCOUNTANT", "Accountant"), ("TEACHER", "Teacher"), ("PARENT", "Parent"), ("STUDENT", "Student")], default="STUDENT", max_length=30)),
    ]
