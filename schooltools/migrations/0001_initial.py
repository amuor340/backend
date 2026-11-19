from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),("schools","0002_backfill_legacy_school")]
    operations=[migrations.CreateModel(name="AuditEvent",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("method",models.CharField(max_length=10)),("path",models.CharField(max_length=500)),("status_code",models.PositiveSmallIntegerField(default=200)),("ip_address",models.GenericIPAddressField(blank=True,null=True)),("created_at",models.DateTimeField(auto_now_add=True,db_index=True)),("actor",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name="audit_events",to=settings.AUTH_USER_MODEL)),("school",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name="audit_events",to="schools.school"))],options={"ordering":["-created_at"]})]
