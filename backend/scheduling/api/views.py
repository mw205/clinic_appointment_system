from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date

from accounts.models import DoctorProfile
from scheduling.api.serializers import (
    DoctorScheduleModelSerializer,
    DoctorSlotModelSerializer,
    ScheduleExceptionModelSerializer
)
from scheduling.models import DoctorSchedule, DoctorSlot, ScheduleException
from scheduling.services.availability_service import AvailabilityService


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleModelSerializer


class DoctorSlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DoctorSlot.objects.all()
    serializer_class = DoctorSlotModelSerializer

    @action(detail=False, methods=["get"], url_path="available")
    def available(self, request):
        doctor_id = request.query_params.get("doctor_id")
        start_date_str = request.query_params.get("start_date")

        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not start_date_str:
            return Response({"error": "start_date is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
            start_date = date.fromisoformat(start_date_str)
        except (DoctorProfile.DoesNotExist, ValueError):
            return Response({"error": "Invalid doctor_id or date format (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)

        available_slots = AvailabilityService.get_available_slots(
            doctor=doctor,
            start_date=start_date
        )
        serializer = self.get_serializer(available_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduleExceptionViewSet(viewsets.ModelViewSet):
    queryset = ScheduleException.objects.all()
    serializer_class = ScheduleExceptionModelSerializer
