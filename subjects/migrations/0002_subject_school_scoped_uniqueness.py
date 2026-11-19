import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("subjects", "0001_initial"), ("schools", "0001_initial")]
    operations = [
        migrations.AddField(model_name="subject", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="subjects", to="schools.school")),
        migrations.AlterField(model_name="subject", name="name", field=models.CharField(max_length=100)),
        migrations.AlterField(model_name="subject", name="code", field=models.CharField(max_length=20)),
        migrations.AddConstraint(model_name="subject", constraint=models.UniqueConstraint(fields=("school", "name"), name="unique_school_subject_name")),
        migrations.AddConstraint(model_name="subject", constraint=models.UniqueConstraint(fields=("school", "code"), name="unique_school_subject_code")),
    ]
