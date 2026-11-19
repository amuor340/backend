from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import ClassAssignment, TeacherAssignment
from .homework_serializers import ClassAssignmentSerializer
from accounts.models import CustomUser
from notifiations.models import Notification


class ClassAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = ClassAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ClassAssignment.objects.select_related("school", "classroom", "subject", "created_by")
        if user.role == CustomUser.Role.SUPER_ADMIN:
            return qs
        if not user.school_id:
            return qs.none()
        if user.role == CustomUser.Role.PARENT:
            return qs.filter(school_id=user.school_id, classroom__students__parent__user=user).distinct()
        if user.role == CustomUser.Role.STUDENT:
            return qs.filter(school_id=user.school_id, classroom__students__user=user).distinct()
        if user.role == CustomUser.Role.TEACHER:
            try:
                return qs.filter(school_id=user.school_id).filter(Q(created_by=user) | Q(classroom__teacher_assignments__teacher=user.teacher_profile, classroom__teacher_assignments__is_active=True)).distinct()
            except Exception:
                return qs.filter(school_id=user.school_id, created_by=user)
        return qs.filter(school_id=user.school_id)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in [CustomUser.Role.SUPER_ADMIN, CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.ACADEMIC_COORDINATOR, CustomUser.Role.TEACHER]:
            raise PermissionDenied("Only teachers and authorized school staff can publish assignments.")
        classroom = serializer.validated_data["classroom"]
        subject = serializer.validated_data["subject"]
        if not classroom.school_id:
            raise PermissionDenied("Assign the classroom to a school before creating homework.")
        if user.role != CustomUser.Role.SUPER_ADMIN:
            if not user.school_id or classroom.school_id != user.school_id or subject.school_id != user.school_id:
                raise PermissionDenied("Classroom and subject must belong to your school.")
            if user.role == CustomUser.Role.TEACHER:
                allowed = TeacherAssignment.objects.filter(teacher__user=user, classroom=classroom, subject=subject, is_active=True).exists()
                if not allowed:
                    raise PermissionDenied("You can only assign work to classes and subjects assigned to you.")
        assignment = serializer.save(school=classroom.school, created_by=user)
        parent_users = CustomUser.objects.filter(
            school_id=assignment.school_id,
            role=CustomUser.Role.PARENT,
            parent_profile__children__classroom=assignment.classroom,
        ).distinct()
        notifications = [Notification(
            recipient=parent,
            triggered_by=user,
            notification_type=Notification.NotificationType.GENERAL,
            title=f"New assignment: {assignment.title}",
            message=f"New work for {assignment.classroom}: {assignment.title}. Due date: {assignment.due_date or 'Not specified'}. Sign in to Pseudosphere to view the instructions.",
        ) for parent in parent_users]
        Notification.objects.bulk_create(notifications)

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if user.role not in [CustomUser.Role.SUPER_ADMIN, CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.ACADEMIC_COORDINATOR, CustomUser.Role.TEACHER]:
            raise PermissionDenied("Only teachers and authorized school staff can update assignments.")
        if user.role == CustomUser.Role.TEACHER and instance.created_by_id != user.id:
            raise PermissionDenied("You can only update assignments you created.")
        classroom = serializer.validated_data.get("classroom", instance.classroom)
        subject = serializer.validated_data.get("subject", instance.subject)
        if not classroom.school_id:
            raise PermissionDenied("The classroom must belong to a school.")
        if user.role != CustomUser.Role.SUPER_ADMIN:
            if classroom.school_id != user.school_id or subject.school_id != user.school_id:
                raise PermissionDenied("Classroom and subject must belong to your school.")
        if user.role == CustomUser.Role.TEACHER:
            allowed = TeacherAssignment.objects.filter(teacher__user=user, classroom=classroom, subject=subject, is_active=True).exists()
            if not allowed:
                raise PermissionDenied("You can only assign work to classes and subjects assigned to you.")
        serializer.save(school=classroom.school)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role not in [CustomUser.Role.SUPER_ADMIN, CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.ACADEMIC_COORDINATOR, CustomUser.Role.TEACHER]:
            raise PermissionDenied("Only teachers and authorized school staff can delete assignments.")
        if user.role == CustomUser.Role.TEACHER and instance.created_by_id != user.id:
            raise PermissionDenied("You can only delete assignments you created.")
        instance.delete()
