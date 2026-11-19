from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication


class PlatformBoundaryJWTAuthentication(JWTAuthentication):
    """
    Keep platform-level SUPER_ADMIN accounts out of school-operational APIs.
    Platform administration is served through /api/schools/ and messaging APIs.
    """
    SCHOOL_OPERATIONAL_PREFIXES = (
        "/api/students/",
        "/api/classes/",
        "/api/subjects/",
        "/api/assignments/",
        "/api/timetable/",
        "/api/attendance/",
        "/api/exams/",
        "/api/results/",
        "/api/reports/",
        "/api/fees/",
        "/api/parents/",
        "/api/dashboard/",
        "/api/anouncements/",
        "/api/accounts/users/",
        "/api/accounts/parents/",
        "/api/accounts/teacher-profiles/",
        "/api/accounts/student-profile/",
        "/api/accounts/student-profilesmoan/",
        "/api/accounts/coordinator-profile/",
        "/api/accounts/teacher-profile/",
        "/api/accounts/accountant-profile/",
        "/api/accounts/parent-profile/",
        "/api/accounts/register/",
        "/api/accounts/reset-password/",
    )

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, validated_token = result
        path = request.path_info
        if getattr(user, "role", None) == "SUPER_ADMIN" and path.startswith(self.SCHOOL_OPERATIONAL_PREFIXES):
            raise PermissionDenied(
                "The Pseudosphere System Admin cannot access school-operational APIs. "
                "Use the platform dashboard and school messaging tools instead."
            )
        return user, validated_token
