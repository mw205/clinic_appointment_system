from datetime import timezone

from rest_framework import serializers

from accounts.api.serializers import DoctorProfileModelSerializer, PatientProfileModelSerializer
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

class AppointmentSerializer(serializers.ModelSerializer):
    waiting_time = serializers.SerializerMethodField()
    doctor = DoctorProfileModelSerializer(read_only=True)
    patient = PatientProfileModelSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor",
            "patient",
            "start_time",
            "end_time",
            "check_in_time",
            "status",
            "waiting_time"
        ]

    def get_waiting_time(self, obj):
        if obj.check_in_time:
            delta = obj.check_in_time - obj.start_time
        else:
            delta = timezone.now() - obj.start_time

        return max(int(delta.total_seconds() / 60), 0)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")
        user = request.user if request else None

        if not user:
            return data

        role = getattr(user, "role", None)

        if role == "patient":
            data.pop("patient", None)

        elif role == "doctor":
            data.pop("doctor", None)

        elif role == "receptionist":
            pass

        return data