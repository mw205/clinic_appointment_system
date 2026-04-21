from rest_framework import serializers

from accounts.models import User
from appointments.models import Appointment
from scheduling.models import DoctorSlot


class AppointmentBookingRequestSerializer(serializers.Serializer):
    slot_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorSlot.objects.all(),
        source="slot",
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="patient"),
        source="patient",
        required=False,
    )


class AppointmentBookingResponseSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(read_only=True)
    patient = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]
