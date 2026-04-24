from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework.permissions import BasePermission


class IsDoctorOrReceptionist(BasePermission):
    message = "Only Doctor or Receptionist can access can view schedules"

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and
            user.is_authenticated and
            getattr(user, "role", None) in {"doctor", "receptionist"}
        )
