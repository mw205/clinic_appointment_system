from rest_framework.permissions import BasePermission

from accounts.rbac import (
    is_patient,
    is_doctor,
    is_receptionist,
    is_admin,
    user_has_any_group,
    PATIENT,
    RECEPTIONIST,
   
)

class IsPatientOrReceptionistRole(BasePermission):
    message = "Only patients or receptionists can book appointments."

    def has_permission(self, request, view):
        return user_has_any_group(
            request.user, [PATIENT, RECEPTIONIST]
        )

class IsDoctorRole(BasePermission):
    message = "Only doctors allowed to make this request."
    def has_permission(self, request, view):
        return is_doctor(request.user)
    

class IsReceptionistRole(BasePermission):
    message = "Only receptionists allowed to make this request."
    def has_permission(self, request, view):
        return is_receptionist(request.user)


class CanCancelAppointment(BasePermission):
    message = "You do not have permission to cancel this appointment."

    def has_object_permission(self, request, view, appointment):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        
        if is_admin(user) or is_receptionist(user):
            return True

    
        if is_patient(user):
            return appointment.patient.user_id == user.id

        return False