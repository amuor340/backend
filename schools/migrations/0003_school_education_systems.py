from django.db import migrations, models

import schools.models


class Migration(migrations.Migration):

    dependencies = [
        ("schools", "0002_backfill_legacy_school"),
    ]

    operations = [
        migrations.AddField(
            model_name="school",
            name="education_systems",
            field=models.JSONField(blank=True, default=schools.models.default_education_systems),
        ),
    ]
