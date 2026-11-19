from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import HomeworkSubmission, ClassAssignment
from .submission_serializers import HomeworkSubmissionSerializer
from accounts.models import CustomUser

class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = HomeworkSubmission.objects.select_related("assignment", "student", "graded_by")
        if user.role == CustomUser.Role.SUPER_ADMIN:
            return qs
        if not user.school_id:
            return qs.none()
        qs = qs.filter(assignment__school_id=user.school_id)
        if user.role == CustomUser.Role.STUDENT:
            return qs.filter(student__user=user)
        if user.role == CustomUser.Role.PARENT:
            return qs.filter(student__parent__user=user)
        if user.role == CustomUser.Role.TEACHER:
            return qs.filter(assignment__classroom__teacher_assignments__teacher__user=user, assignment__classroom__teacher_assignments__is_active=True).distinct()
        if user.role in [CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.ACADEMIC_COORDINATOR]:
            return qs
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != CustomUser.Role.STUDENT:
            raise PermissionDenied("Only students can submit homework.")
        try:
            student = user.student_record
        except Exception:
            from students.models import Student
            student = Student.objects.filter(user=user).first()
        if not student:
            raise ValidationError("No student record is linked to this login. Ask your school administrator to link it.")
        assignment = serializer.validated_data["assignment"]
        if assignment.classroom_id != student.classroom_id:
            raise PermissionDenied("You can only submit work assigned to your own class.")
        if HomeworkSubmission.objects.filter(assignment=assignment, student=student).exists():
            raise ValidationError("You have already submitted this assignment. Contact your teacher if you need to replace it.")
        due = assignment.due_date
        status = HomeworkSubmission.Status.LATE if due and due < timezone.localdate() else HomeworkSubmission.Status.SUBMITTED
        serializer.save(student=student, status=status)

    def perform_update(self, serializer):
        user = self.request.user
        submission = self.get_object()
        if user.role == CustomUser.Role.STUDENT:
            if submission.student.user_id != user.id or submission.status in [HomeworkSubmission.Status.GRADED, HomeworkSubmission.Status.RETURNED]:
                raise PermissionDenied("This submission can no longer be edited.")
            serializer.save()
            return
        if user.role not in [CustomUser.Role.TEACHER, CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.ACADEMIC_COORDINATOR]:
            raise PermissionDenied("You cannot grade this submission.")
        if user.role == CustomUser.Role.TEACHER and not submission.assignment.classroom.teacher_assignments.filter(teacher__user=user, is_active=True, subject=submission.assignment.subject).exists():
            raise PermissionDenied("You are not assigned to this class and subject.")
        serializer.save(graded_by=user, status=HomeworkSubmission.Status.GRADED if serializer.validated_data.get("grade") is not None else HomeworkSubmission.Status.RETURNED)

    def perform_destroy(self, instance):
        raise PermissionDenied("Homework submissions are retained for school records.")
