from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import ClassRoom
from .serializers import ClassRoomSerializer
from accounts.permisions import IsAdminOrAcademicCoordinator


class ClassRoomListView(generics.ListAPIView):
    queryset = ClassRoom.objects.select_related(
        "class_teacher",
        "class_teacher__user",
    ).order_by("-created_at")

    serializer_class = ClassRoomSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "grade",
        "stream",
    ]

    search_fields = [
        "grade",
        "stream",
        "class_teacher__user__first_name",
        "class_teacher__user__last_name",
    ]

    def get_queryset(self):
        qs = ClassRoom.objects.select_related("class_teacher", "class_teacher__user").order_by("-created_at")
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            qs = qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs

    ordering_fields = [
        "grade",
        "stream",
        "capacity",
        "created_at",
    ]


class ClassRoomDetailView(generics.RetrieveAPIView):
    queryset = ClassRoom.objects.select_related("class_teacher", "class_teacher__user")

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs

    serializer_class = ClassRoomSerializer
    permission_classes = [IsAuthenticated]


class ClassRoomCreateView(generics.CreateAPIView):
    queryset = ClassRoom.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "SUPER_ADMIN":
            serializer.save()
        elif user.school_id:
            serializer.save(school_id=user.school_id)
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Your account is not assigned to a school.")

    serializer_class = ClassRoomSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]


class ClassRoomUpdateView(generics.UpdateAPIView):

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs
    queryset = ClassRoom.objects.select_related(
        "class_teacher",
        "class_teacher__user",
    )

    serializer_class = ClassRoomSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]

    # Allows both PUT and PATCH
    http_method_names = [
        "put",
        "patch",
        "options",
        "head",
    ]


class ClassRoomDeleteView(generics.DestroyAPIView):

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role != "SUPER_ADMIN":
            return qs.filter(school_id=user.school_id) if user.school_id else qs.none()
        return qs
    queryset = ClassRoom.objects.all()

    serializer_class = ClassRoomSerializer

    permission_classes = [
        IsAdminOrAcademicCoordinator
    ]

    http_method_names = [
        "delete",
        "options",
        "head",
    ]