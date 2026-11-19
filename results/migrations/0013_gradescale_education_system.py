from decimal import Decimal

from django.db import migrations, models

# Frozen copy of the starter bands so this migration never changes if
# schools/education.py is edited later. Kenya CBC rows are left untouched.
_SEED = {
    "KENYA_HIGH_SCHOOL": [
        ("A", "Excellent", "80", "100", "Excellent performance."),
        ("A-", "Very Good", "75", "79.99", "Very good performance."),
        ("B+", "Very Good", "70", "74.99", "Very good performance."),
        ("B", "Good", "65", "69.99", "Good performance."),
        ("B-", "Good", "60", "64.99", "Good performance."),
        ("C+", "Satisfactory", "55", "59.99", "Satisfactory - keep improving."),
        ("C", "Satisfactory", "50", "54.99", "Average performance."),
        ("C-", "Fair", "45", "49.99", "Fair - more effort needed."),
        ("D+", "Weak", "40", "44.99", "Weak - needs consistent revision."),
        ("D", "Weak", "35", "39.99", "Weak - needs support."),
        ("D-", "Poor", "30", "34.99", "Poor - needs urgent support."),
        ("E", "Very Poor", "0", "29.99", "Very poor - immediate intervention needed."),
    ],
    "SOUTH_SUDAN_PRIMARY": [
        ("A", "Excellent", "75", "100", "Excellent performance."),
        ("B", "Very Good", "60", "74.99", "Very good performance."),
        ("C", "Good", "45", "59.99", "Good - satisfactory performance."),
        ("D", "Pass", "31", "44.99", "Pass - needs improvement."),
        ("F", "Fail", "0", "30.99", "Fail - below the pass mark."),
    ],
}
_SEED["SOUTH_SUDAN_SECONDARY"] = _SEED["SOUTH_SUDAN_PRIMARY"]

_COMMENTS = {
    "A": "An outstanding result. Keep up the excellent work.",
    "A-": "A very strong result. A little more effort will reach the top band.",
    "B+": "Very good work. Keep pushing for excellence.",
    "B": "Good work. Consistent revision will lift this further.",
    "B-": "Good effort. Focus on the weaker topics to improve.",
    "C+": "A satisfactory result with clear room to grow.",
    "C": "An average result. More practice is needed.",
    "C-": "Fair effort. Regular revision and support are advised.",
    "D+": "Performance is weak. Please work closely with the subject teacher.",
    "D": "Performance is weak and needs sustained support.",
    "D-": "Performance is poor. Urgent support is recommended.",
    "E": "Performance is very poor. Immediate intervention is needed.",
    "F": "Below the pass mark. Extra support and tutoring are strongly advised.",
}


def seed_scales(apps, schema_editor):
    GradeScale = apps.get_model("results", "GradeScale")
    ReportComment = apps.get_model("results", "ReportComment")
    for system, rows in _SEED.items():
        if GradeScale.objects.filter(education_system=system).exists():
            continue
        for level, description, low, high, remarks in rows:
            scale = GradeScale.objects.create(
                education_system=system,
                level=level,
                description=description,
                minimum_score=Decimal(low),
                maximum_score=Decimal(high),
                remarks=remarks,
            )
            ReportComment.objects.create(grade=scale, comment=_COMMENTS[level])


def unseed_scales(apps, schema_editor):
    GradeScale = apps.get_model("results", "GradeScale")
    GradeScale.objects.filter(education_system__in=list(_SEED)).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0012_alter_learningoutcome_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="gradescale",
            name="education_system",
            field=models.CharField(db_index=True, default="KENYA_CBC", max_length=30),
        ),
        migrations.AlterField(
            model_name="gradescale",
            name="level",
            field=models.CharField(max_length=5),
        ),
        migrations.AddConstraint(
            model_name="gradescale",
            constraint=models.UniqueConstraint(
                fields=("education_system", "level"), name="unique_grade_level_per_system"
            ),
        ),
        migrations.RunPython(seed_scales, unseed_scales),
    ]
