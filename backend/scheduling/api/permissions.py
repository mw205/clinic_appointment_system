from rest_framework.permissions import BasePermission

from accounts.rbac import user_has_any_group, DOCTOR, RECEPTIONIST


class IsDoctorOrReceptionist(BasePermission):
    message = "Only Doctor or Receptionist can access or view schedules."

    def has_permission(self, request, view):
        return user_has_any_group(
            request.user,
            [DOCTOR, RECEPTIONIST]
        )