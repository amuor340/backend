import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("anouncements", "0003_announcement_recipient"), ("schools", "0001_initial")]
    operations = [migrations.AddField(model_name="announcement", name="school", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="announcements", to="schools.school"))]
