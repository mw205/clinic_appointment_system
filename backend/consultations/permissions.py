from  rest_framework.permissions import BasePermission
from accounts.rbac import is_doctor, is_patient , is_admin
from appointments.models import Appointment


def is_consultation_doctor(user, consultation):

    return bool(
        user
        and user.is_authenticated
        and consultation.appointment.doctor.user_id == user.id
    )

def is_consultation_patient(user, consultation):
    return bool(
        user
        and user.is_authenticated
        and consultation.appointment.patient.user_id == user.id
    )

class IsDoctor(BasePermission):
    message = "Only doctors can perform this action."

    def has_permission(self, request, view):
        return is_doctor(request.user)

    def has_object_permission(self, request, view, obj):
        return is_consultation_doctor(request.user, obj)

class IsPatient(BasePermission):
    message = "Only patients can perform this action."

    def has_permission(self, request, view):
        return is_patient(request.user)

    def has_object_permission(self, request, view, obj):
        return is_consultation_patient(request.user, obj)

class IsAdmin(BasePermission):
    message = "Only admins can perform this action."
    def has_permission(self, request, view):
        return is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        return is_admin(request.user)

class IsDoctorOrAdmin(BasePermission):
    message = "Only the doctor who created the consultation or admins can perform this action."
    def has_permission(self, request, view):
        return is_doctor(request.user) or is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        return is_admin(request.user) or is_consultation_doctor(request.user,obj)