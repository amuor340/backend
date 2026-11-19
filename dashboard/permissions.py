from accounts.permissions import RolePermission
from accounts.models import CustomUser


class HasRolePermission(RolePermission):
    """Compatibility alias for app-specific role permissions."""


class IsSuperAdmin(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SUPER_ADMIN,
    ]


class IsAcademicCoordinator(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.ACADEMIC_COORDINATOR,
    ]


class IsAccountant(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.ACCOUNTANT,
    ]


class IsTeacher(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.TEACHER,
    ]


class IsParent(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.PARENT,
    ]


class IsAdminOrAcademicCoordinator(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.ACADEMIC_COORDINATOR,
    ]


class IsAdminOrAccountant(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.ACCOUNTANT,
    ]


class IsAdminOrTeacher(HasRolePermission):
    allowed_roles = [
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.TEACHER,
    ]


class IsDashboardUser(HasRolePermission):
    """
    Any authenticated staff member allowed to view the dashboard.
    """

    allowed_roles = [
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.ACADEMIC_COORDINATOR,
        CustomUser.Role.ACCOUNTANT,
        CustomUser.Role.TEACHER,
    ]