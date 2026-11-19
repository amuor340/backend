import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("classes", "0004_alter_classroom_grade"), ("schools", "0001_initial")]
    operations = [
        migrations.AddField(model_name="classroom", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="classrooms", to="schools.school")),
        migrations.RemoveConstraint(model_name="classroom", name="unique_grade_stream"),
        migrations.AddConstraint(model_name="classroom", constraint=models.UniqueConstraint(fields=("school", "grade", "stream"), name="unique_school_grade_stream")),
    ]
