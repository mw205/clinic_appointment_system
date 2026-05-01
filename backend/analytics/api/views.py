import csv

from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from appointments.models import Appointment
from consultations.models import ConsultationRecord
from analytics.api.permissions import IsAdmin
from analytics.api.serializers import AnalyticsSummaryModelSerializer

class AnalyticsSummaryViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        total = Appointment.objects.count()
        total_consultations = ConsultationRecord.objects.count()
        no_show_count = Appointment.objects.filter(
            status = Appointment.Status.NO_SHOW
        ).count()
        if no_show_count > 0:
            no_show_rate = round(no_show_count / total * 100,2)
        else:
            no_show_rate = 0

        group_by_status = list(
            Appointment.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        group_by_hour = list(
            Appointment.objects.annotate(hour=ExtractHour("start_time"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("hour")
        )
        data ={
            "total_appointments": total,
            "total_consultations": total_consultations,
            "no_show_rate": no_show_rate,
            "appointment_status_counts": group_by_status,
            "peak_hours": group_by_hour,
        }
        serializer = AnalyticsSummaryModelSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="export/appointments")
    def export_appointments(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="appointments.csv"'
        writer = csv.writer(response)
        writer.writerow(["ID", "Patient", "Doctor", "Start Time", "End Time", "Status"])
        appointments = Appointment.objects.select_related(
            "patient__user",
            "doctor__user",
        ).all()

        for appt in appointments:
            writer.writerow([
                appt.id,
                appt.patient.user.get_full_name(),
                appt.doctor.user.get_full_name(),
                appt.start_time,
                appt.end_time,
                appt.status,
            ])
        return response

    @action(detail=False, methods=["get"], url_path="export/consultations")
    def export_consultations(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="consultations.csv"'
        writer = csv.writer(response)
        writer.writerow(["ID", "Appointment ID", "Patient", "Doctor", "Diagnosis", "Completed", "Completed At",])
        consultations = ConsultationRecord.objects.select_related(
            "appointment__patient__user",
            "appointment__doctor__user",
        ).all()

        for c in consultations:
            writer.writerow([
                c.id,
                c.appointment.id,
                c.appointment.patient.user.get_full_name(),
                c.appointment.doctor.user.get_full_name(),
                c.diagnosis,
                c.is_completed,
                c.completed_at,
            ])
        return response

