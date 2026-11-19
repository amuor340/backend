from rest_framework import generics, filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import TeacherProfile
from accounts.serializers import TeacherProfilePublicSerializer
from .models import TeacherAssignment
from .serializers import (
    TeacherAssignmentSerializer,
    TeacherProfileSerializer,
)
from accounts.permisions import IsAdminOrAcademicCoordinator


# ============================================================
# PUBLIC TEACHER LIST — FOR DROPDOWNS
# ============================================================

class TeacherProfileListView(generics.ListAPIView):
    """
    Returns teachers who have active assignments.

    This endpoint is used for teacher dropdowns.

    Uses the public serializer so sensitive teacher information
    such as national ID and date of birth is not exposed.
    """

    serializer_class = TeacherProfilePublicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = TeacherProfile.objects.filter(assignments__is_active=True).distinct().select_related("user")
        user = self.request.user
        if user.role != "SUPER_ADMIN":
            qs = qs.filter(user__school_id=user.school_id) if user.school_id else qs.none()
        return qs


# ============================================================
# TEACHER'S OWN ASSIGNMENTS
# ============================================================

class MyTeacherAssignmentsView(generics.ListAPIView):
    """
    Returns ONLY the TeacherAssignment records belonging
    to the currently logged-in teacher.
    """

    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        try:
            teacher_profile = user.teacher_profile
        except TeacherProfile.DoesNotExist:
            return TeacherAssignment.objects.none()

        return (
            TeacherAssignment.objects
            .filter(teacher=teacher_profile, is_active=True, classroom__school_id=user.school_id)
            .select_related(
                "teacher__user",
                "classroom",
                "subject",
            )
            .order_by(
                "-academic_year",
                "term",
                "classroom__grade",
                "classroom__stream",
                "subject__name",
            )
        )


# ============================================================
# ASSIGNMENT CREATE — ADMIN / ACADEMIC COORDINATOR
# ============================================================

class TeacherAssignmentCreateView(generics.CreateAPIView):

    queryset = TeacherAssignment.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        classroom = serializer.validated_data.get("classroom")
        teacher = serializer.validated_data.get("teacher")
        subject = serializer.validated_data.get("subject")
        if user.role != "SUPER_ADMIN" and (not user.school_id or classroom.school_id != user.school_id or subject.school_id != user.school_id or teacher.user.school_id != user.school_id):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Teacher, subject, and classroom must belong to your school.")
        serializer.save()

    serializer_class = TeacherAssignmentSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]


# ============================================================
# ASSIGNMENT LIST
# ============================================================

class TeacherAssignmentListView(generics.ListAPIView):

    serializer_class = TeacherAssignmentSerializer

    permission_classes = [
        IsAuthenticated
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "teacher",
        "classroom",
        "subject",
        "term",
        "academic_year",
        "is_active",
        "is_class_teacher",
    ]

    search_fields = [
        "teacher__user__first_name",
        "teacher__user__last_name",
        "teacher__user__username",
        "subject__name",
        "classroom__grade",
        "classroom__stream",
    ]

    ordering_fields = [
        "academic_year",
        "term",
        "assigned_date",
        "created_at",
    ]

    ordering = [
        "-created_at"
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = TeacherAssignment.objects.select_related("teacher__user", "classroom", "subject")
        if user.role != "SUPER_ADMIN":
            if not user.school_id:
                return queryset.none()
            queryset = queryset.filter(classroom__school_id=user.school_id)
        if user.role in ["SUPER_ADMIN", "SCHOOL_ADMIN", "ACADEMIC_COORDINATOR"]:
            return queryset
        if user.role == "TEACHER":
            return queryset.filter(teacher__user=user, is_active=True)
        return TeacherAssignment.objects.none()


# ============================================================
# ASSIGNMENT DETAIL
# ============================================================

class TeacherAssignmentDetailView(generics.RetrieveAPIView):

    def get_queryset(self):
        qs = TeacherAssignment.objects.all()
        user = self.request.user
        if user.role != "SUPER_ADMIN":
            return qs.filter(classroom__school_id=user.school_id) if user.school_id else qs.none()
        return qs

    queryset = (
        TeacherAssignment.objects
        .select_related(
            "teacher__user",
            "classroom",
            "subject",
        )
    )

    serializer_class = TeacherAssignmentSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]


# ============================================================
# ASSIGNMENT UPDATE
# ============================================================

class TeacherAssignmentUpdateView(generics.UpdateAPIView):

    def get_queryset(self):
        qs = TeacherAssignment.objects.all()
        user = self.request.user
        if user.role != "SUPER_ADMIN":
            return qs.filter(classroom__school_id=user.school_id) if user.school_id else qs.none()
        return qs

    queryset = TeacherAssignment.objects.all()

    serializer_class = TeacherAssignmentSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]


# ============================================================
# ASSIGNMENT DELETE
# ============================================================

class TeacherAssignmentDeleteView(generics.DestroyAPIView):

    def get_queryset(self):
        qs = TeacherAssignment.objects.all()
        user = self.request.user
        if user.role != "SUPER_ADMIN":
            return qs.filter(classroom__school_id=user.school_id) if user.school_id else qs.none()
        return qs

    queryset = TeacherAssignment.objects.all()

    serializer_class = TeacherAssignmentSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]


# ============================================================
# TEACHER PROFILE VIEWSET
# ============================================================

class TeacherProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Logged-in teacher's own profile.

    /assignments/my-profile/

    This endpoint returns only the currently authenticated
    teacher's profile.
    """

    serializer_class = TeacherProfileSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return TeacherProfile.objects.filter(
            user=self.request.user
        ) 