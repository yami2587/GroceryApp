from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    """
    Allows access only to users with is_manager True.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_manager)
