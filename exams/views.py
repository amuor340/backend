from rest_framework import generics

from .models import Exam
from .serializers import ExamSerializer
from accounts.permisions import IsAdminOrAcademicCoordinator


# =====================================================
# CREATE
# =====================================================

class ExamCreateView(generics.CreateAPIView):
    queryset = Exam.objects.select_related("classroom", "subject")

    def get_queryset(self):
        qs = Exam.objects.select_related("classroom", "subject")
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(classroom__school_id=user.school_id, subject__school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = ExamSerializer

    permission_classes = [IsAdminOrAcademicCoordinator]

    def perform_create(self, serializer):
        user = self.request.user
        classroom = serializer.validated_data.get("classroom")
        subject = serializer.validated_data.get("subject")
        if user.role != "SUPER_ADMIN" and (not user.school_id or classroom.school_id != user.school_id or subject.school_id != user.school_id):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Exam classroom and subject must belong to your school.")
        serializer.save()


# =====================================================
# LIST
# =====================================================

class ExamListView(generics.ListAPIView):
    queryset = Exam.objects.select_related("classroom", "subject")

    def get_queryset(self):
        qs = Exam.objects.select_related("classroom", "subject")
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(classroom__school_id=user.school_id, subject__school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = ExamSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]


# =====================================================
# DETAIL
# =====================================================

class ExamDetailView(generics.RetrieveAPIView):
    queryset = Exam.objects.select_related("classroom", "subject")

    def get_queryset(self):
        qs = Exam.objects.select_related("classroom", "subject")
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(classroom__school_id=user.school_id, subject__school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = ExamSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]


# =====================================================
# UPDATE
# =====================================================

class ExamUpdateView(generics.UpdateAPIView):
    queryset = Exam.objects.select_related("classroom", "subject")

    def get_queryset(self):
        qs = Exam.objects.select_related("classroom", "subject")
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(classroom__school_id=user.school_id, subject__school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = ExamSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]


# =====================================================
# DELETE
# =====================================================

class ExamDeleteView(generics.DestroyAPIView):
    queryset = Exam.objects.select_related("classroom", "subject")

    def get_queryset(self):
        qs = Exam.objects.select_related("classroom", "subject")
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(classroom__school_id=user.school_id, subject__school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = ExamSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]