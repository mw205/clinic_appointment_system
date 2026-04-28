from rest_framework.permissions import BasePermission

from accounts.rbac import is_admin, is_receptionist

class IsAdminOrReceptionist(BasePermission):
    message = "Only admin or receptionist users can access this resource."

    def has_permission(self, request, view):
        user = request.user
        return is_admin(user) or is_receptionist(user)