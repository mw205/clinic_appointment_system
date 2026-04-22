import django_filters

from appointments.models import Appointment


class AppointmentFilter(django_filters.FilterSet):
    doctor_id = django_filters.NumberFilter(field_name="doctor_id")
    patient_id = django_filters.NumberFilter(field_name="patient_id")
    start_from = django_filters.IsoDateTimeFilter(
        field_name="start_time",
        lookup_expr="gte",
    )
    start_to = django_filters.IsoDateTimeFilter(
        field_name="start_time",
        lookup_expr="lte",
    )

    class Meta:
        model = Appointment
        fields = ["status", "doctor_id", "patient_id", "start_from", "start_to"]
