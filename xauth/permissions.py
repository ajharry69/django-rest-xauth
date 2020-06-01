from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated


class IsOwnerOrSuperuser(IsAuthenticated):
    """
    Allows access only to authenticated users who own the object(s)
    in question.

    ================================================================

    DO NOT USE THIS FOR PERMISSION CHECK OUT OF USER MODEL SCOPE
    ================================================================
    """

    # message = "specify custom message on permission rejected"

    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(obj.id == user.id or user and user.is_superuser)


class IsOwnerOrSuperuserOrReadOnly(IsOwnerOrSuperuser):

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            super().has_permission(request, view)
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            super().has_object_permission(request, view, obj)
        )


class IsSuperUserOrReadOnly(BasePermission):
    """
    Allows WRITE privilege only to superuser(s) and READ to everyone else.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.is_superuser
        )
