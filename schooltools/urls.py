from django.urls import path
from .views import SchoolAlertsView, AuditEventsView, StudentExportView
urlpatterns = [path("alerts/", SchoolAlertsView.as_view(), name="school-alerts"), path("audit-events/", AuditEventsView.as_view(), name="audit-events"), path("exports/students.csv", StudentExportView.as_view(), name="students-csv-export")]
