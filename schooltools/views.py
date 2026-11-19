import csv
from datetime import timedelta
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from accounts.models import CustomUser
from assignments.models import ClassAssignment
from attendance.models import Attendance
from students.models import Student
from .models import AuditEvent

STAFF = {CustomUser.Role.SUPER_ADMIN, CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.ACADEMIC_COORDINATOR}

class SchoolAlertsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user=request.user
        if not user.school_id and user.role != CustomUser.Role.SUPER_ADMIN: return Response({"alerts": []})
        today=timezone.localdate(); soon=today+timedelta(days=3)
        tasks=ClassAssignment.objects.filter(due_date__gte=today, due_date__lte=soon)
        absences=Attendance.objects.filter(status="Absent", submission__date=today)
        if user.role != CustomUser.Role.SUPER_ADMIN:
            tasks=tasks.filter(school_id=user.school_id); absences=absences.filter(submission__classroom__school_id=user.school_id)
        if user.role == CustomUser.Role.TEACHER:
            tasks=tasks.filter(classroom__teacher_assignments__teacher__user=user).distinct()
        if user.role == CustomUser.Role.PARENT:
            tasks=tasks.filter(classroom__students__parent__user=user).distinct()
            absences=absences.filter(student__parent__user=user)
        if user.role == CustomUser.Role.STUDENT:
            tasks=tasks.filter(classroom__students__user=user).distinct()
            absences=absences.filter(student__user=user)
        alerts=[]
        for task in tasks.order_by("due_date")[:100]: alerts.append({"type":"deadline", "id":task.pk, "title":task.title, "message":f"Due {task.due_date}", "date":str(task.due_date)})
        for row in absences.select_related("student")[:100]: alerts.append({"type":"absence", "id":row.pk, "title":f"Absence: {row.student.first_name} {row.student.last_name}", "message":f"Marked absent on {row.submission.date}", "date":str(row.submission.date)})
        return Response({"alerts":alerts, "count":len(alerts)})

class AuditEventsView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        user=request.user
        if user.role not in STAFF: raise PermissionDenied("Only school administrators and academic coordinators can view audit activity.")
        qs=AuditEvent.objects.select_related("actor")
        if user.role != CustomUser.Role.SUPER_ADMIN: qs=qs.filter(school_id=user.school_id)
        data=[{"id":e.pk,"actor":e.actor.get_full_name() if e.actor else "Former user","method":e.method,"path":e.path,"status_code":e.status_code,"created_at":e.created_at} for e in qs[:200]]
        return Response({"results":data})

class StudentExportView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        user=request.user
        if user.role not in STAFF and user.role != CustomUser.Role.ACCOUNTANT: raise PermissionDenied("You are not allowed to export school records.")
        qs=Student.objects.select_related("classroom","parent")
        if user.role != CustomUser.Role.SUPER_ADMIN: qs=qs.filter(school_id=user.school_id)
        response=HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"]='attachment; filename="pseudosphere-students.csv"'
        writer=csv.writer(response); writer.writerow(["Admission number","First name","Last name","Class","Gender","Date of birth","Status"])
        for s in qs.iterator(): writer.writerow([s.admission_number,s.first_name,s.last_name,str(s.classroom),s.gender,s.date_of_birth,s.status])
        return response
