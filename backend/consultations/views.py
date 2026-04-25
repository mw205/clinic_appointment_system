from django.shortcuts import render
from rest_framework import viewsets , status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.rbac import is_doctor
from .models import ConsultationRecord
from .serializers import ConsultationRecordSerializer, ConsultationSummarySerializer
from .permissions import IsDoctor, IsPatient, IsDoctorOrAdmin

class ConsultationRecordViewSet(viewsets.ModelViewSet):

    serializer = ConsultationRecordSerializer
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update' , 'destroy']:
            return [IsDoctor()]
        return [IsDoctorOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if is_doctor(user):
            return ConsultationRecord.objects.filter(appointment__doctor=user)
        else:
            return ConsultationRecord.objects.filter(appointment__patient=user)
