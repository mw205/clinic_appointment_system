from rest_framework import serializers

from accounts.api.serializers import DoctorProfileModelSerializer
from accounts.models import DoctorProfile
from scheduling.models import DoctorSchedule, ScheduleException


class DoctorScheduleModelSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileModelSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source="doctor",
        write_only=True,
    )
    target_date = serializers.DateField(required=False, allow_null=True, default=None)
    day_of_week = serializers.CharField(required=False)

    class Meta:
        model = DoctorSchedule
        fields = [
            "id",
            "doctor",
            "doctor_id",
            "target_date",
            "day_of_week",
            "start_time",
            "end_time",
            "slot_duration_minutes",
            "buffer_time_minutes",
            "updated_at",
            "created_at",
        ]
        read_only_fields = ["id", "updated_at", "created_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        target_date = None

        if hasattr(instance, "target_date") and instance.target_date:
            target_date = instance.target_date

        if not target_date and instance.day_of_week:
            target_date = self._get_next_date_for_day(instance.day_of_week)

        if hasattr(target_date, "isoformat"):
            target_date = target_date.isoformat()

        representation["target_date"] = target_date
        return representation

    def _get_next_date_for_day(self, day_name):
        from datetime import date, timedelta

        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        try:
            target_day_idx = days.index(day_name.lower())
        except ValueError:
            return None

        today = date.today()
        current_day_idx = today.weekday()  # Monday is 0, Sunday is 6

        days_ahead = target_day_idx - current_day_idx
        if days_ahead < 0:
            days_ahead += 7

        return today + timedelta(days_ahead)

    def validate(self, attrs):
        target_date = attrs.get("target_date", None)
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        day_of_week = attrs.get("day_of_week", getattr(self.instance, "day_of_week", None))
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))

        if target_date is not None:
            derived_day = target_date.strftime("%A").lower()
            if day_of_week and day_of_week != derived_day:
                raise serializers.ValidationError(
                    {
                        "day_of_week": (
                            f"day_of_week ({day_of_week}) does not match target_date "
                            f"({target_date.isoformat()} -> {derived_day})."
                        )
                    }
                )
            attrs["day_of_week"] = derived_day
            day_of_week = derived_day

        if not day_of_week and not target_date:
            raise serializers.ValidationError(
                {"day_of_week": "This field is required if target_date is not provided."}
            )

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

    def create(self, validated_data):
        # Strip non-model field(s)
        target_date = validated_data.pop("target_date", None)
        instance = super().create(validated_data)
        instance.target_date = target_date
        return instance

    def update(self, instance, validated_data):
        target_date = validated_data.pop("target_date", None)
        instance = super().update(instance, validated_data)
        instance.target_date = target_date
        return instance


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
        exception_type = attrs.get("exception_type", getattr(self.instance, "exception_type", None))
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))

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
