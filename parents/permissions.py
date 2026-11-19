from accounts.permissions import RolePermission
from accounts.models import CustomUser


class IsSuperAdmin(RolePermission):
    allowed_roles = (CustomUser.Role.SUPER_ADMIN,)
