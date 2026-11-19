from django.db import migrations


def backfill_legacy_school(apps, schema_editor):
    School = apps.get_model("schools", "School")
    User = apps.get_model("accounts", "CustomUser")
    ClassRoom = apps.get_model("classes", "ClassRoom")
    Subject = apps.get_model("subjects", "Subject")
    Student = apps.get_model("students", "Student")
    Announcement = apps.get_model("anouncements", "Announcement")

    school, _ = School.objects.get_or_create(
        slug="legacy-luma-school",
        defaults={
            "name": "Luma 2000 Academy",
            "email": "legacy-school-contact@example.invalid",
            "status": "APPROVED",
        },
    )
    # Preserve legacy school records and attach them to one tenant. Existing
    # platform SUPER_ADMIN accounts remain unscoped for platform operations.
    User.objects.filter(school__isnull=True).exclude(role="SUPER_ADMIN").update(school_id=school.pk)
    ClassRoom.objects.filter(school__isnull=True).update(school_id=school.pk)
    Subject.objects.filter(school__isnull=True).update(school_id=school.pk)
    Student.objects.filter(school__isnull=True).update(school_id=school.pk)
    Announcement.objects.filter(school__isnull=True).update(school_id=school.pk)


def noop_reverse(apps, schema_editor):
    # Intentionally keep backfilled ownership if migration is reversed; removing
    # it could make records visible across tenants.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("schools", "0001_initial"),
        ("accounts", "0004_customuser_school_and_school_admin"),
        ("classes", "0005_classroom_school_tenant_constraint"),
        ("subjects", "0002_subject_school_scoped_uniqueness"),
        ("students", "0009_student_school_scoped_admission"),
        ("anouncements", "0004_announcement_school"),
    ]
    operations = [migrations.RunPython(backfill_legacy_school, noop_reverse)]
