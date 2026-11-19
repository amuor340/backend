from accounts.permissions import RolePermission
from accounts.models import CustomUser

class HasRolePermission(RolePermission):
    """Compatibility alias for report-specific role policies."""
    

class IsSuperAdmin(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SUPER_ADMIN,
    ]


class IsAcademicCoordinator(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SUPER_ADMIN,
        CustomUser.Role.ACADEMIC_COORDINATOR,
    ]


class IsAccountant(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SUPER_ADMIN,
        CustomUser.Role.ACCOUNTANT,
    ]


class IsTeacher(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SUPER_ADMIN,
        CustomUser.Role.TEACHER,
    ]





