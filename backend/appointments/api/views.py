from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.api.permissions import IsPatientOrReceptionistRole
from appointments.api.serializers import (
    AppointmentBookingRequestSerializer,
    AppointmentBookingResponseSerializer,
)
from appointments.models import Appointment
from appointments.services.booking_service import create_appointment_from_slot


class AppointmentBookingCreateAPIView(APIView):
    permission_classes = [IsPatientOrReceptionistRole]

    def post(self, request):
        serializer = AppointmentBookingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient_user = self.resolve_booking_patient_user(request, serializer.validated_data)

        try:
            appointment = create_appointment_from_slot(
                patient=patient_user,
                slot=serializer.validated_data["slot"],
            )
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise ValidationError(exc.message_dict)
            raise ValidationError({"detail": exc.messages})

        response_serializer = AppointmentBookingResponseSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def resolve_booking_patient_user(self, request, validated_data):
        requester = request.user
        requester_role = getattr(requester, "role", None)

        if requester_role == "patient":
            requested_patient = validated_data.get("patient")
            if requested_patient is not None and requested_patient.id != requester.id:
                raise PermissionDenied("Patients can only book appointments for themselves.")
            return requester

        if requester_role == "receptionist":
            requested_patient = validated_data.get("patient")
            if requested_patient is None:
                raise ValidationError({"patient_id": "This field is required for receptionists."})
            return requested_patient



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm(request, id):
    try:
        appointment = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        raise NotFound("Appointment not found")

    if not request.user.has_perm("appointments.change_appointment"):
        raise PermissionDenied("You do not have permission")
    if appointment.doctor.user_id != request.user.id:
        raise PermissionDenied("You do not have permission")

    if appointment.status != Appointment.Status.REQUESTED:
        return Response({"error": "Appointment already processed"}, status=400)

    appointment.status = Appointment.Status.CONFIRMED
    appointment.save(update_fields=["status"])

    return Response({"message": "Appointment confirmed"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel(request, id):
    try:
        appointment = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        raise NotFound("Appointment not found")

    if not request.user.has_perm("appointments.change_appointment"):
        raise PermissionDenied("You do not have permission")
    if appointment.patient.user_id != request.user.id:
        raise PermissionDenied("You do not have permission")

    if appointment.status == Appointment.Status.COMPLETED:
        return Response({"error": "Appointment already completed"}, status=400)

    appointment.status = Appointment.Status.CANCELLED
    appointment.save(update_fields=["status"])

    return Response({"message": "Appointment cancelled"})
