from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.rbac import is_admin, is_doctor
from accounts.models import DoctorProfile
from appointments.models import Appointment
from consultations.api.permissions import IsDoctor, IsDoctorOrAdmin, IsPatient
from consultations.api.serializers import (
    ConsultationRecordModelSerializer,
    ConsultationSummaryModelSerializer,
    PrescriptionItemModelSerializer,
    RequestedTestModelSerializer,
)
from consultations.models import ConsultationRecord, PrescriptionItem, RequestedTest

class ConsultationRecordViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultationRecordModelSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'complete']:
            return [IsDoctor()]
        if self.action == 'summary':
            return [IsPatient()]
        return [IsDoctorOrAdmin()]

    def get_queryset(self):
        user = self.request.user

        if is_doctor(user):
            return ConsultationRecord.objects.filter(
                appointment__doctor__user=user,
            )
        if is_admin(user):
            return ConsultationRecord.objects.all()

        return ConsultationRecord.objects.none()

    def perform_create(self, serializer):
        doctor_profile = get_object_or_404(DoctorProfile, user=self.request.user)
        serializer.save(doctor=doctor_profile)

    @action(detail=True, methods=['post'])
    def complete(self, request):
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
            appointment.save(update_fields=["updated_at","status"])

        return Response(ConsultationRecordModelSerializer(consultation).data)

    @action(detail=True, methods=["GET"])
    def summary(self, request):
        consultation = self.get_object()
        if consultation.appointment.patient.user_id != request.user.id:
            return Response(
                {"detail": "You can only view your own consultation."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(ConsultationSummaryModelSerializer(consultation).data)

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


