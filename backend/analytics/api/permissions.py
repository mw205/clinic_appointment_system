from rest_framework.permissions import BasePermission
from accounts.rbac import user_has_any_group, ADMIN

class IsAdmin(BasePermission):
    message = "Only Admin users can access this resource"
    def has_permission(self, request, view):
        return user_has_any_group(request.user, [ADMIN])