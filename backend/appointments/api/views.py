from datetime import datetime

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.migrations import serializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, GenericViewSet

from appointments.exceptions import BookingBadRequestError
from appointments.api.permissions import IsPatientOrReceptionistRole, IsDoctorRole, IsReceptionistRole
from appointments.api.serializers import (
    AppointmentBookingRequestSerializer,
    AppointmentBookingResponseSerializer, AppointmentSerializer,
)
from appointments.models import Appointment
from appointments.services.booking_service import create_appointment_from_slot
from appointments.services.queue_service import get_doctor_queue


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
            raise BookingBadRequestError.from_django_validation_error(exc)

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
                raise BookingBadRequestError("patient_id is required for receptionists.")
            return requested_patient


class AppointmentViewSet(GenericViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentBookingResponseSerializer
    # TODO: uncomment function bellow after authentication is implemented
    # def get_permissions(self):
    #     if self.action == "confirm":
    #         return [IsDoctorRole()]
    #     if self.action == "cancel":
    #         return [IsPatientOrReceptionistRole]
    #     if self.action == "check_in":
    #         return [IsReceptionistRole]
    #     return [IsAuthenticated()]


    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        if not request.user.has_perm("appointments.change_appointment"):
            raise PermissionDenied("You do not have permission")
        if appointment.doctor.user_id != request.user.id:
            raise PermissionDenied("You do not have permission")

        if appointment.status != Appointment.Status.REQUESTED:
            return Response({"error": "Appointment already processed"}, status=HTTP_400_BAD_REQUEST)

        appointment.status = Appointment.Status.CONFIRMED
        appointment.save(update_fields=["status"])

        return Response({"message": "Appointment confirmed"}, status=HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()

        if not request.user.has_perm("appointments.change_appointment"):
            raise PermissionDenied("You do not have permission")
        if appointment.patient.user_id != request.user.id:
            raise PermissionDenied("You do not have permission")

        if appointment.status == Appointment.Status.COMPLETED:
            return Response({"error": "Appointment already completed"}, status=HTTP_400_BAD_REQUEST)

        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status"])

        return Response({"message": "Appointment cancelled"}, status=HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        appointment = self.get_object()

        if not request.user.has_perm("appointments.change_appointment"):
            raise PermissionDenied("You do not have permission")
        if appointment.status != Appointment.Status.REQUESTED:
            return Response({"error": "Appointment already processed"}, status=HTTP_400_BAD_REQUEST)
        appointment.status = Appointment.Status.CHECKED_IN
        appointment.check_in_time = datetime.now()
        appointment.save()
        return Response({"message": "Appointment checked in"}, HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='doctor/queue', url_name='doctor-queue')
    def doctor_queue(self, request):
        doctor = request.user
        date = request.GET.get('date')
        queue = get_doctor_queue(doctor.id, date)
        queue_serializer = AppointmentSerializer(queue, many=True, context={"request": request})
        return Response(
            queue_serializer.data,
            status=HTTP_200_OK
        )