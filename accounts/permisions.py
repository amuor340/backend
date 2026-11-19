"""Backward-compatible import path. New code should use accounts.permissions."""
from accounts.permissions import RolePermission
from accounts.models import CustomUser


class IsAdminOrAcademicCoordinator(RolePermission):
    allowed_roles = (
        CustomUser.Role.SUPER_ADMIN,
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.ACADEMIC_COORDINATOR,
    )
