from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.rbac import is_admin, is_doctor
from accounts.models import DoctorProfile
from appointments.models import Appointment
from consultations.api.permissions import IsDoctor, IsDoctorOrAdmin
from consultations.api.serializers import (
    ConsultationRecordModelSerializer,
    PrescriptionItemModelSerializer,
    RequestedTestModelSerializer,
)
from consultations.models import ConsultationRecord, PrescriptionItem, RequestedTest

class ConsultationRecordViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultationRecordModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["appointment"]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'complete']:
            return [IsDoctor()]
        if self.action == 'by_appointment':
            return [IsAuthenticated()]
        if self.action == 'summary':
            return [IsAuthenticated()]
        return [IsDoctorOrAdmin()]

    def get_queryset(self):
        user = self.request.user

        if is_doctor(user):
            return ConsultationRecord.objects.filter(
                appointment__doctor__user=user,
            )
        if self.action in {"summary", "by_appointment"}:
            return ConsultationRecord.objects.filter(
                appointment__patient__user=user,
            )
        if is_admin(user):
            return ConsultationRecord.objects.all()

        return ConsultationRecord.objects.none()

    def perform_create(self, serializer):
        doctor_profile = get_object_or_404(DoctorProfile, user=self.request.user)
        serializer.save(doctor=doctor_profile)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        consultation = self.get_object()
        if consultation.is_completed:
            return Response({"detail" : "Consultation is already completed"}
                            ,status=status.HTTP_400_BAD_REQUEST)

        appointment = consultation.appointment
        if appointment.status != Appointment.Status.CHECKED_IN:
            return Response({"detail" : "Appointment must be checked in before it can be completed."}
                            , status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            consultation.completed_at = timezone.now()
            appointment.status = Appointment.Status.COMPLETED
            consultation.save(update_fields=["completed_at", "updated_at"])
            appointment.save(update_fields=["status"])

        return Response(ConsultationRecordModelSerializer(consultation).data)

    @action(detail=True, methods=["GET"])
    def summary(self, request, pk=None):
        try:
            consultation_id = int(pk)
        except (TypeError, ValueError):
            raise NotFound("Consultation summary not found.")

        consultation = ConsultationRecord.objects.filter(
            id=consultation_id,
            appointment__patient__user_id=request.user.id,
        ).values("id", "appointment_id", "diagnosis", "completed_at").first()
        if not consultation:
            raise NotFound("Consultation summary not found.")

        prescription_items = list(
            PrescriptionItem.objects.filter(consultation_id=consultation["id"]).values(
                "id",
                "drug",
                "dose",
                "duration",
                "instructions",
            )
        )
        requested_tests = list(
            RequestedTest.objects.filter(consultation_id=consultation["id"]).values(
                "id",
                "test_name",
                "notes",
            )
        )

        return Response(
            {
                "id": consultation["id"],
                "appointment": consultation["appointment_id"],
                "diagnosis": consultation["diagnosis"],
                "is_completed": consultation["completed_at"] is not None,
                "prescription_items": prescription_items,
                "requested_tests": requested_tests,
            }
        )

    @action(detail=False, methods=["GET"], url_path=r"by-appointment/(?P<appointment_id>[^/.]+)")
    def by_appointment(self, request, appointment_id=None):
        consultation = get_object_or_404(
            ConsultationRecord.objects.only("id"),
            appointment_id=appointment_id,
            appointment__patient__user_id=request.user.id,
        )
        return Response({"id": consultation.id})

class PrescriptionItemViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionItemModelSerializer
    permission_classes = [IsDoctor]
    filterset_fields = ["consultation"]

    def get_queryset(self):
        return PrescriptionItem.objects.filter(
            consultation__appointment__doctor__user=self.request.user
        )

    def perform_create(self, serializer):
        consultation = get_object_or_404(
            ConsultationRecord,
            id = self.request.data.get('consultation'),
            appointment__doctor__user = self.request.user,
        )
        serializer.save(consultation=consultation)


class RequestedTestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestedTestModelSerializer
    permission_classes = [IsDoctor]
    filterset_fields = ["consultation"]

    def get_queryset(self):
        return RequestedTest.objects.filter(
            consultation__appointment__doctor__user=self.request.user
        )

    def perform_create(self, serializer):
        consultation = get_object_or_404(
            ConsultationRecord,
            id=self.request.data.get("consultation"),
            appointment__doctor__user=self.request.user,
        )
        serializer.save(consultation=consultation)


