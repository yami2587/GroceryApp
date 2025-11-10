from rest_framework.permissions import BasePermission
#permission for allowing only managers to have acces to is_manager
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', '') == 'manager')
