import django.db.models.deletion
from django.db import migrations, models


def backfill_profile_schools(apps, schema_editor):
    for model_name in ["ParentProfile", "TeacherProfile", "AccountantProfile", "AcademicCoordinatorProfile", "StudentProfile"]:
        Model = apps.get_model("accounts", model_name)
        for profile in Model.objects.filter(school__isnull=True).select_related("user").iterator():
            if profile.user_id and profile.user.school_id:
                Model.objects.filter(pk=profile.pk).update(school_id=profile.user.school_id)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_customuser_school_and_school_admin"),
        ("schools", "0002_backfill_legacy_school"),
    ]
    operations = [
        migrations.AddField(model_name="parentprofile", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="parent_profiles", to="schools.school")),
        migrations.AddField(model_name="teacherprofile", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="teacher_profiles", to="schools.school")),
        migrations.AddField(model_name="accountantprofile", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="accountant_profiles", to="schools.school")),
        migrations.AddField(model_name="academiccoordinatorprofile", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="coordinator_profiles", to="schools.school")),
        migrations.AddField(model_name="studentprofile", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="student_profiles", to="schools.school")),
        migrations.AlterField(model_name="teacherprofile", name="employee_number", field=models.CharField(max_length=30)),
        migrations.AlterField(model_name="teacherprofile", name="national_id", field=models.CharField(max_length=20)),
        migrations.AlterField(model_name="accountantprofile", name="employee_number", field=models.CharField(max_length=30)),
        migrations.AlterField(model_name="academiccoordinatorprofile", name="employee_number", field=models.CharField(max_length=30)),
        migrations.AlterField(model_name="studentprofile", name="admission_number", field=models.CharField(max_length=30)),
        migrations.AlterField(model_name="studentprofile", name="national_id", field=models.CharField(blank=True, max_length=20, null=True)),
        migrations.AddConstraint(model_name="teacherprofile", constraint=models.UniqueConstraint(fields=("school", "employee_number"), name="unique_school_teacher_employee_number")),
        migrations.AddConstraint(model_name="teacherprofile", constraint=models.UniqueConstraint(fields=("school", "national_id"), name="unique_school_teacher_national_id")),
        migrations.AddConstraint(model_name="accountantprofile", constraint=models.UniqueConstraint(fields=("school", "employee_number"), name="unique_school_accountant_employee_number")),
        migrations.AddConstraint(model_name="academiccoordinatorprofile", constraint=models.UniqueConstraint(fields=("school", "employee_number"), name="unique_school_coordinator_employee_number")),
        migrations.AddConstraint(model_name="studentprofile", constraint=models.UniqueConstraint(fields=("school", "admission_number"), name="unique_school_student_profile_admission")),
        migrations.AddConstraint(model_name="studentprofile", constraint=models.UniqueConstraint(fields=("school", "national_id"), name="unique_school_student_profile_national_id")),
        migrations.RunPython(backfill_profile_schools, noop_reverse),
    ]
