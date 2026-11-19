from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Subject
from .serializers import SubjectSerializer
from accounts.permisions import IsAdminOrAcademicCoordinator


class SubjectListView(generics.ListAPIView):
    def get_queryset(self):
        qs = Subject.objects.all()
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "code",
    ]

    search_fields = [
        "name",
        "code",
    ]

    ordering_fields = [
        "name",
        "code",
        "created_at",
    ]


class SubjectDetailView(generics.RetrieveAPIView):
    def get_queryset(self):
        qs = Subject.objects.all()
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class SubjectCreateView(generics.CreateAPIView):
    def get_queryset(self):
        qs = Subject.objects.all()
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "SUPER_ADMIN":
            serializer.save()
        elif user.school_id:
            serializer.save(school_id=user.school_id)
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Your account is not assigned to a school.")

    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrAcademicCoordinator]


class SubjectUpdateView(generics.UpdateAPIView):
    def get_queryset(self):
        qs = Subject.objects.all()
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrAcademicCoordinator]


class SubjectDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        qs = Subject.objects.all()
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrAcademicCoordinator] 