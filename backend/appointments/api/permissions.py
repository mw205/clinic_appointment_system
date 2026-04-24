from rest_framework.permissions import BasePermission


class IsPatientOrReceptionistRole(BasePermission):
    message = "Only patients or receptionists can book appointments."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in {"patient", "receptionist"}
        )

class IsDoctorRole(BasePermission):
    message = "Only doctors allowed to make this request."
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "doctor"
        )
class IsReceptionistRole(BasePermission):
    message = "Only receptionists allowed to make this request."
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name="Receptionist").exists()
        )


class CanCancelAppointment(BasePermission):
    message = "You do not have permission to cancel this appointment."

    def has_object_permission(self, request, view, appointment):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        user_role = user.role.lower()

        if user_role == "admin":
            return True
        if user_role == "receptionist":
            return True
        if user_role == "patient":
            return appointment.patient.user_id == user.id
        return False
