from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from appointments.api.filters import AppointmentFilter
from appointments.api.pagination import AppointmentListPagination
from appointments.api.permissions import IsPatientOrReceptionistRole
from appointments.api.serializers import (
    AppointmentBookingRequestSerializer,
    AppointmentBookingResponseSerializer,
    AppointmentReadSerializer,
)
from appointments.exceptions import BookingBadRequestError
from appointments.models import Appointment
from appointments.services.booking_service import create_appointment_from_slot


def get_role_filtered_appointments_queryset(user):
    queryset = Appointment.objects.select_related(
        "patient__user",
        "doctor__user",
    )

    group_names = {
        name.strip().lower()
        for name in user.groups.values_list("name", flat=True)
    }
    user_role = (getattr(user, "role", "") or "").lower()
    user_roles = set(group_names)
    if user_role:
        user_roles.add(user_role)

    if user.is_staff or "admin" in user_roles:
        return queryset
    if "receptionist" in user_roles:
        return queryset
    if "doctor" in user_roles:
        return queryset.filter(doctor__user=user)
    if "patient" in user_roles:
        return queryset.filter(patient__user=user)
    return queryset.none()


class AppointmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Appointment.objects.none()
    pagination_class = AppointmentListPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AppointmentFilter
    ordering_fields = ["start_time", "created_at"]
    ordering = ["-start_time"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsPatientOrReceptionistRole()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AppointmentBookingRequestSerializer
        return AppointmentReadSerializer

    def get_queryset(self):
        return get_role_filtered_appointments_queryset(self.request.user)

    def create(self, request):
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

        raise PermissionDenied("You do not have permission to book appointments.")


class AppointmentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = AppointmentReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_role_filtered_appointments_queryset(self.request.user)


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
