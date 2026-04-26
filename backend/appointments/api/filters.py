import django_filters

from appointments.models import Appointment


class AppointmentFilter(django_filters.FilterSet):
    doctor_id = django_filters.NumberFilter(field_name="doctor_id")
    patient_id = django_filters.NumberFilter(field_name="patient_id")

    patient_name = django_filters.CharFilter(
        field_name="patient__user__username",
        lookup_expr="icontains"
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
        fields = ["status", "doctor_id", "patient_id", "start_from", "start_to", "patient_name", "date"]
