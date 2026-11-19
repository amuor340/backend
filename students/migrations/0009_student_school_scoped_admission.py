import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("students", "0008_student_user"), ("schools", "0001_initial")]
    operations = [
        migrations.AddField(model_name="student", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="students", to="schools.school")),
        migrations.AlterField(model_name="student", name="admission_number", field=models.CharField(db_index=True, max_length=20)),
        migrations.AlterField(model_name="student", name="assessment_number", field=models.CharField(blank=True, db_index=True, max_length=20, null=True)),
        migrations.AddConstraint(model_name="student", constraint=models.UniqueConstraint(fields=("school", "admission_number"), name="unique_school_admission_number")),
        migrations.AddConstraint(model_name="student", constraint=models.UniqueConstraint(fields=("school", "assessment_number"), name="unique_school_assessment_number")),
    ]
