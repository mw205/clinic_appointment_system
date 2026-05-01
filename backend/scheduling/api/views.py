from datetime import datetime

from accounts.models import DoctorProfile
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from scheduling.api.permissions import IsDoctorOrReceptionist
from scheduling.api.serializers import (
    DoctorScheduleModelSerializer,
    ScheduleExceptionModelSerializer,
)
from scheduling.models import DoctorSchedule, ScheduleException
from scheduling.services.availability_service import AvailabilityService


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleModelSerializer
    filterset_fields = ["doctor", "day_of_week"]
    permission_classes = [IsAuthenticated, IsDoctorOrReceptionist]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "available"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsDoctorOrReceptionist()]

    @action(
        detail=False,
        methods=["GET"],
        url_path="available",
        permission_classes=[AllowAny],
    )
    def available(self, request):
        doctor_id = request.query_params.get("doctor_id")
        date = request.query_params.get("date")

        if not doctor_id:
            raise ValidationError(
                "doctor_id is required", code=status.HTTP_400_BAD_REQUEST
            )
        if not date:
            raise ValidationError("date is required", code=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(
                "date is invalid, it should be like this 2026-05-01",
                code=status.HTTP_400_BAD_REQUEST,
            )

        doctor = get_object_or_404(DoctorProfile, id=doctor_id)

        available_slots = AvailabilityService.get_available_slots(doctor, target_date)
        return Response(available_slots, status=status.HTTP_200_OK)


class ScheduleExceptionViewSet(viewsets.ModelViewSet):
    queryset = ScheduleException.objects.all()
    serializer_class = ScheduleExceptionModelSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrReceptionist]
