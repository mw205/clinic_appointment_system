from rest_framework.permissions import BasePermission
from accounts.rbac import user_has_any_group, DOCTOR, ADMIN, PATIENT

class IsDoctor(BasePermission):
    message = "Only doctors can perform this action."
    def has_permission(self, request, view):
        return user_has_any_group(request.user, [DOCTOR])

class IsPatient(BasePermission):
    message = "Only patients can perform this action."
    def has_permission(self, request, view):
        return user_has_any_group(request.user, [PATIENT])

class IsDoctorOrAdmin(BasePermission):
    message = "Only doctors or admins can perform this action."
    def has_permission(self, request, view):
        return user_has_any_group(request.user, [DOCTOR, ADMIN])