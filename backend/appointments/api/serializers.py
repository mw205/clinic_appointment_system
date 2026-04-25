from django.utils import timezone
from rest_framework import serializers

from accounts.api.serializers import (
    DoctorProfileModelSerializer,
    PatientProfileModelSerializer,
)
from accounts.models import DoctorProfile, User
from appointments.models import Appointment
from accounts.rbac import PATIENT, is_doctor, is_patient


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
    queryset=User.objects.filter(groups__name=PATIENT),
    source="patient",
    required=False,
    )


class AppointmentRescheduleRequestSerializer(serializers.Serializer):
    new_start_time = serializers.DateTimeField()
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
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
            "waiting_time",
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

        if not user or not user.is_authenticated:
            return data

        if is_patient(user):
            data.pop("patient", None)
        elif is_doctor(user):
            data.pop("doctor", None)

        return data
