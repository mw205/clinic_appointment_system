from rest_framework import viewsets

from scheduling.api.serializers import (
    DoctorScheduleModelSerializer,
    ScheduleExceptionModelSerializer,
)
from scheduling.models import DoctorSchedule, ScheduleException


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleModelSerializer


class ScheduleExceptionViewSet(viewsets.ModelViewSet):
    queryset = ScheduleException.objects.all()
    serializer_class = ScheduleExceptionModelSerializer
