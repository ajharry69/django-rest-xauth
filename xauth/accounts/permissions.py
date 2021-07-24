from rest_framework import permissions

__all__ = ["IsOwner"]


class IsOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.pk == obj.pk
