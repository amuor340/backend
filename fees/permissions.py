from accounts.permissions import RolePermission
from accounts.models import CustomUser


class IsSuperAdmin(RolePermission):
    allowed_roles = (CustomUser.Role.SUPER_ADMIN,)


class IsAccountant(RolePermission):
    allowed_roles = (CustomUser.Role.ACCOUNTANT,)


class IsSuperAdminOrAccountant(RolePermission):
    allowed_roles = (
        CustomUser.Role.SUPER_ADMIN,
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.ACCOUNTANT,
    )


class IsAcademicCoordinator(RolePermission):
    allowed_roles = (CustomUser.Role.ACADEMIC_COORDINATOR,)


class IsSuperAdminAccountantOrAcademicCoordinator(RolePermission):
    allowed_roles = (
        CustomUser.Role.SUPER_ADMIN,
        CustomUser.Role.SCHOOL_ADMIN,
        CustomUser.Role.ACCOUNTANT,
        CustomUser.Role.ACADEMIC_COORDINATOR,
    )
