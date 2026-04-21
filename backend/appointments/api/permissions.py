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
