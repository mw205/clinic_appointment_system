import django_filters
from django.db.models import Q

from appointments.models import Appointment


class AppointmentFilter(django_filters.FilterSet):
    doctor_id = django_filters.NumberFilter(field_name="doctor_id")
    patient_id = django_filters.NumberFilter(field_name="patient_id")

    patient_name = django_filters.CharFilter(method='filter_patient_name')
    doctor_name = django_filters.CharFilter(method='filter_doctor_name')

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            Q(patient__user__first_name__icontains=value) |
            Q(patient__user__last_name__icontains=value)
        )

    def filter_doctor_name(self, queryset, name, value):
        return queryset.filter(
            Q(doctor__user__first_name__icontains=value) |
            Q(doctor__user__last_name__icontains=value)
        )

    start_from = django_filters.IsoDateTimeFilter(
        field_name="start_time",
        lookup_expr="gte",
    )
    start_to = django_filters.IsoDateTimeFilter(
        field_name="start_time",
        lookup_expr="lte",
    )
    status = django_filters.ChoiceFilter(choices=Appointment.Status.choices)
    date = django_filters.DateFilter(field_name="start_time", lookup_expr="date")

    class Meta:
        model = Appointment
        fields = ["status", "doctor_id", "patient_id", "start_from", "start_to", "patient_name", "date", "doctor_name"]
