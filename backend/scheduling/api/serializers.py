from rest_framework import serializers

from accounts.api.serializers import DoctorProfileModelSerializer
from accounts.models import DoctorProfile
from scheduling.models import DoctorSchedule, DoctorSlot, ScheduleException


class DoctorScheduleModelSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileModelSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source="doctor",
        write_only=True,
    )

    class Meta:
        model = DoctorSchedule
        fields = [
            "id",
            "doctor",
            "doctor_id",
            "day_of_week",
            "start_time",
            "end_time",
            "slot_duration_minutes",
            "buffer_time_minutes",
            "updated_at",
            "created_at",
        ]
        read_only_fields = ["id", "updated_at", "created_at"]

    def validate(self, attrs):
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        day_of_week = attrs.get("day_of_week", getattr(self.instance, "day_of_week", None))
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )

        if doctor and day_of_week and start_time and end_time:
            overlapping_schedules = DoctorSchedule.objects.filter(
                doctor=doctor,
                day_of_week=day_of_week,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance:
                overlapping_schedules = overlapping_schedules.exclude(id=self.instance.id)
            if overlapping_schedules.exists():
                raise serializers.ValidationError(
                    "This doctor already has a schedule during this time."
                )

        return attrs


class DoctorSlotModelSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileModelSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source="doctor",
        write_only=True,
    )

    class Meta:
        model = DoctorSlot
        fields = [
            "id",
            "doctor",
            "doctor_id",
            "schedule",
            "exception",
            "start_time",
            "end_time",
            "is_available",
            "appointment",
            "updated_at",
            "created_at",
        ]
        read_only_fields = ["id", "updated_at", "created_at", "appointment"]


class ScheduleExceptionModelSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileModelSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source="doctor",
        write_only=True,
    )

    class Meta:
        model = ScheduleException
        fields = [
            "id",
            "doctor",
            "doctor_id",
            "exception_date",
            "exception_type",
            "start_time",
            "end_time",
            "slot_duration_minutes",
            "buffer_time_minutes",
            "reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        exception_type = attrs.get('exception_type', getattr(self.instance, 'exception_type', None))
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))

        if exception_type == ScheduleException.ExceptionType.WORK:
            if not start_time or not end_time:
                raise serializers.ValidationError(
                    "Working exceptions must have start and end times."
                )
            if start_time >= end_time:
                raise serializers.ValidationError(
                    {"end_time": "End time must be after start time."}
                )
        return attrs
