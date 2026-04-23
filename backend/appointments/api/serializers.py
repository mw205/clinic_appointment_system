from rest_framework import serializers

from accounts.models import DoctorProfile
from accounts.models import User
from appointments.models import Appointment


class AppointmentReadSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()

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

    def get_patient(self, obj):
        patient_user = obj.patient.user
        return {
            "id": obj.patient_id,
            "user_id": patient_user.id,
            "name": patient_user.get_full_name() or patient_user.username,
        }

    def get_doctor(self, obj):
        doctor_user = obj.doctor.user
        return {
            "id": obj.doctor_id,
            "user_id": doctor_user.id,
            "name": doctor_user.get_full_name() or doctor_user.username,
        }


class AppointmentBookingRequestSerializer(serializers.Serializer):
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source="doctor",
    )
    start_time = serializers.DateTimeField()
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

class DoctorQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor",
            "start_time",
            "end_time",
            "check_in_time",
            "patient"
        ]
