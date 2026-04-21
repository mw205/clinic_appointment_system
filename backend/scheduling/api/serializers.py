from rest_framework import serializers

from accounts.api.serializers import DoctorProfileModelSerializer
from accounts.models import DoctorProfile
from scheduling.models import DoctorSchedule


class DoctorScheduleModelSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileModelSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source='doctor',
        write_only=True,
    )

    class Meta:
        fields = [
            'id',
            'doctor',
            'doctor_id',
            'day_of_week',
            'start_time',
            'end_time',
            'updated_at',
            'created_at',
        ]
        read_only_fields = ['updated_at', 'created_at', 'id']
        model = DoctorSchedule

        def validate(self, attrs):
            start_time = attrs.get("start_time")
            end_time = attrs.get("end_time")
            # validate the start time that it can't be after end time
            if start_time and end_time and start_time >= end_time:
                raise serializers.ValidationError({
                    "end_time": "End time must be after start time."
                })

            # ensure that there are no overlapping schedules for the same doctor
            doctor = attrs.get('doctor')
            if doctor and start_time and end_time:
                overlapping_schedules = DoctorSchedule.objects.filter(
                    doctor=doctor,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                )
            if self.instance:
                overlapping_schedules = overlapping_schedules.exclude(
                    id=self.instance.id
                )
            if overlapping_schedules.exists():
                raise serializers.ValidationError(
                    "This doctor already has a schedule during this time."
                )
            return attrs
