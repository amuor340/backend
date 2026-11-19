"""Canonical reusable permission primitives for the Django backend.

Role-specific policies stay in their owning apps; this module centralizes the
repeated authentication/role comparison so those policies cannot drift in code.
"""
from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    """Allow authenticated users whose role is listed in ``allowed_roles``."""

    allowed_roles = ()

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and getattr(user, "role", None) in self.allowed_roles
        )
