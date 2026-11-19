from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from students.models import Student
from classes.models import ClassRoom
from accounts.models import TeacherProfile, ParentProfile
from accounts.models import CustomUser
from subjects.models import Subject
from . import education
from .models import School
from .permissions import IsPlatformSuperAdmin
from .serializers import SchoolRegistrationSerializer, SchoolSerializer, SchoolSettingsSerializer

User = get_user_model()


class SchoolRegistrationView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "school_registration"

    @transaction.atomic
    def post(self, request):
        serializer = SchoolRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        school = School.objects.create(
            name=data["school_name"],
            registration_number=data.get("registration_number", ""),
            email=data["school_email"],
            phone=data.get("school_phone", ""),
            address=data.get("address", ""),
            education_systems=data.get("education_systems") or [education.DEFAULT_SYSTEM],
        )
        # The initial school administrator remains inactive until the platform owner approves the school.
        User.objects.create_user(
            username=data["admin_username"],
            email=data["admin_email"],
            password=data["admin_password"],
            first_name=data["admin_first_name"],
            last_name=data["admin_last_name"],
            role=CustomUser.Role.SCHOOL_ADMIN,
            school=school,
            is_active=False,
        )
        return Response({"message": "Registration submitted. Your school is pending approval.", "school": SchoolSerializer(school).data}, status=status.HTTP_201_CREATED)


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsPlatformSuperAdmin]
    queryset = School.objects.all()

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def approve(self, request, pk=None):
        school = self.get_object()
        if school.status == School.Status.SUSPENDED:
            return Response({"detail": "A suspended school must be reviewed before approval."}, status=status.HTTP_409_CONFLICT)
        school.status = School.Status.APPROVED
        school.rejection_reason = ""
        school.approved_at = timezone.now()
        school.save(update_fields=["status", "rejection_reason", "approved_at", "updated_at"])
        User.objects.filter(school=school, role=CustomUser.Role.SCHOOL_ADMIN).update(is_active=True)
        return Response({"message": "School approved.", "school": self.get_serializer(school).data})

    @action(detail=True, methods=["post"], url_path="assign-admin")
    @transaction.atomic
    def assign_admin(self, request, pk=None):
        school = self.get_object()
        username = str(request.data.get("username", "")).strip()
        if not username:
            return Response({"detail": "Provide the username of an existing account."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username__iexact=username).first()
        if not user:
            return Response({"detail": "No account was found with that username."}, status=status.HTTP_404_NOT_FOUND)
        if user.id == request.user.id or user.role == CustomUser.Role.SUPER_ADMIN:
            return Response({"detail": "A platform administrator cannot be reassigned as a school administrator."}, status=status.HTTP_400_BAD_REQUEST)
        if user.school_id and user.school_id != school.id:
            return Response({"detail": "That account already belongs to another school."}, status=status.HTTP_409_CONFLICT)
        user.school = school
        user.role = CustomUser.Role.SCHOOL_ADMIN
        user.is_active = user.is_active and school.status == School.Status.APPROVED
        user.save(update_fields=["school", "role", "is_active", "updated_at"])
        return Response({"message": "School administrator assigned.", "username": user.username, "active": user.is_active, "school": self.get_serializer(school).data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def reject(self, request, pk=None):
        school = self.get_object()
        reason = str(request.data.get("reason", "")).strip()
        school.status = School.Status.REJECTED
        school.rejection_reason = reason[:4000]
        school.save(update_fields=["status", "rejection_reason", "updated_at"])
        User.objects.filter(school=school, role=CustomUser.Role.SCHOOL_ADMIN).update(is_active=False)
        return Response({"message": "School registration rejected.", "school": self.get_serializer(school).data})


class PlatformDashboardView(APIView):
    """Aggregate platform metrics for the Pseudosphere System Admin only."""
    permission_classes = [IsAuthenticated, IsPlatformSuperAdmin]

    def get(self, request):
        schools = School.objects.all()
        users = User.objects.all()
        return Response({
            "stats": {
                "total_schools": schools.count(),
                "approved_schools": schools.filter(status=School.Status.APPROVED).count(),
                "pending_schools": schools.filter(status=School.Status.PENDING).count(),
                "suspended_schools": schools.filter(status=School.Status.SUSPENDED).count(),
                "rejected_schools": schools.filter(status=School.Status.REJECTED).count(),
                "total_users": users.count(),
                "active_users": users.filter(is_active=True).count(),
                "total_students": Student.objects.count(),
                "total_teachers": TeacherProfile.objects.count(),
                "total_parents": ParentProfile.objects.count(),
                "total_classes": ClassRoom.objects.count(),
            },
            "recent_schools": SchoolSerializer(
                schools.order_by("-created_at")[:8],
                many=True,
                context={"request": request},
            ).data,
        })


class MySchoolView(APIView):
    permission_classes = [IsAuthenticated]

    def _school(self, request):
        school = getattr(request.user, "school", None)
        if not school:
            return None
        return school

    def get(self, request):
        school = self._school(request)
        if not school:
            return Response({"detail": "This account is not assigned to a school."}, status=status.HTTP_404_NOT_FOUND)
        return Response(SchoolSerializer(school, context={"request": request}).data)

    def patch(self, request):
        if request.user.role != CustomUser.Role.SCHOOL_ADMIN:
            return Response({"detail": "Only the school administrator can update school settings."}, status=status.HTTP_403_FORBIDDEN)
        school = self._school(request)
        if not school:
            return Response({"detail": "This account is not assigned to a school."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SchoolSettingsSerializer(school, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(SchoolSerializer(school, context={"request": request}).data)


class EducationSystemsView(APIView):
    """Catalogue of supported curricula: class levels, grade bands, pass marks."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(education.system_catalog())


class StarterSubjectsView(APIView):
    """Create the usual subjects for each curriculum the school teaches (skips existing ones)."""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        if user.role not in (CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.ACADEMIC_COORDINATOR) or not user.school_id:
            return Response({"detail": "Only a school administrator or academic coordinator can do this."}, status=status.HTTP_403_FORBIDDEN)
        school = user.school
        existing_names = {n.lower() for n in Subject.objects.filter(school=school).values_list("name", flat=True)}
        existing_codes = {c.upper() for c in Subject.objects.filter(school=school).values_list("code", flat=True)}
        created = []
        for system in school.education_systems or [education.DEFAULT_SYSTEM]:
            for name, code in education.STARTER_SUBJECTS.get(system, []):
                if name.lower() in existing_names or code.upper() in existing_codes:
                    continue
                Subject.objects.create(school=school, name=name, code=code)
                existing_names.add(name.lower())
                existing_codes.add(code.upper())
                created.append(name)
        return Response({"created": created, "count": len(created)}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
