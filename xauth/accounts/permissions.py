from rest_framework import permissions

__all__ = ["IsOwner", "IsSuperuser"]


class IsOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.pk == obj.pk


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS or request.user and request.user.is_superuser)
