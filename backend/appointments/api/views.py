from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from appointments.api.filters import AppointmentFilter
from appointments.api.pagination import AppointmentListPagination
from appointments.api.permissions import (
    CanCancelAppointment,
    CanRescheduleAppointment,
    IsDoctorRole,
    IsPatientOrReceptionistRole,
)
from appointments.api.serializers import (
    AppointmentBookingRequestSerializer,
    AppointmentBookingResponseSerializer,
    AppointmentReadSerializer,
    AppointmentRescheduleRequestSerializer,
    AppointmentSerializer,
)
from appointments.exceptions import BookingBadRequestError
from appointments.models import Appointment
from appointments.services.booking_service import cancel_appointment, create_appointment
from appointments.services.doctor_appointments_service import get_doctor_appointments
from appointments.services.reschedule_service import reschedule_appointment

from accounts.rbac import ADMIN, RECEPTIONIST, is_receptionist, is_doctor, is_patient, user_has_any_group



def get_role_filtered_appointments_queryset(user):
    queryset = Appointment.objects.select_related(
        "patient__user",
        "doctor__user",
    )

    if not user or not user.is_authenticated:
        return queryset.none()

    if user_has_any_group(user, [ADMIN, RECEPTIONIST]):
        return queryset

    if is_doctor(user):
        return queryset.filter(doctor__user=user)

    if is_patient(user):
        return queryset.filter(patient__user=user)
    return queryset.none()


class AppointmentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Appointment.objects.none()
    pagination_class = AppointmentListPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AppointmentFilter
    ordering_fields = ["start_time", "created_at"]
    ordering = ["-start_time"]

    def get_permissions(self):
        if self.action == "create":
            return [IsPatientOrReceptionistRole()]
        if self.action == "cancel":
            return [IsAuthenticated(), CanCancelAppointment()]
        if self.action == "reschedule":
            return [IsAuthenticated(), CanRescheduleAppointment()]
        if self.action == "doctor_queue":
            return [IsAuthenticated(), IsDoctorRole()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return AppointmentBookingRequestSerializer
        if self.action == "reschedule":
            return AppointmentRescheduleRequestSerializer
        return AppointmentReadSerializer

    def get_queryset(self):
        return get_role_filtered_appointments_queryset(self.request.user)

    def create(self, request):
        serializer = AppointmentBookingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient_user = self.resolve_booking_patient_user(request, serializer.validated_data)

        appointment = create_appointment(
            patient=patient_user,
            doctor=serializer.validated_data["doctor"],
            start_time=serializer.validated_data["start_time"],
        )

        response_serializer = AppointmentBookingResponseSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def resolve_booking_patient_user(self, request, validated_data):
        requester = request.user

        if is_patient(requester):
            requested_patient = validated_data.get("patient")
            if requested_patient is not None and requested_patient.id != requester.id:
                raise PermissionDenied("Patients can only book appointments for themselves.")
            return requester

        if is_receptionist(requester):
            requested_patient = validated_data.get("patient")
            if requested_patient is None:
                raise BookingBadRequestError("patient_id is required for receptionists.")
            return requested_patient

        raise PermissionDenied("You do not have permission to book appointments.")

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

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        self.check_object_permissions(request, appointment)

        appointment = cancel_appointment(
            appointment,
            request.user,
        )
        serializer = AppointmentReadSerializer(appointment)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        appointment = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = reschedule_appointment(
            appointment=appointment,
            new_start_time=serializer.validated_data["new_start_time"],
            changed_by=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        response_serializer = AppointmentReadSerializer(appointment)
        return Response(response_serializer.data)

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

    @action(detail=False, methods=['get'], url_path='doctor/appointments', url_name='doctor-appointments')
    def doctor_appointments(self, request):
        doctor = request.user
        queryset = get_doctor_appointments(doctor.id)
        queryset = self.filter_queryset(queryset)
        queue_serializer = AppointmentSerializer(queryset, many=True, context={"request": request})
        return Response(
            queue_serializer.data,
            status=HTTP_200_OK
        )