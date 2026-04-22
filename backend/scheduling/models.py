from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import DoctorProfile


DAY_OF_WEEK_CHOICES = [
    ("monday", "Monday"),
    ("tuesday", "Tuesday"),
    ("wednesday", "Wednesday"),
    ("thursday", "Thursday"),
    ("friday", "Friday"),
    ("saturday", "Saturday"),
    ("sunday", "Sunday"),
]


class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    day_of_week = models.CharField(max_length=50, choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(10)],
    )
    buffer_time_minutes = models.PositiveIntegerField(
        default=5,
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Start time must be earlier than end time.")

        overlapping_schedules = DoctorSchedule.objects.filter(
            doctor=self.doctor,
            day_of_week=self.day_of_week
        ).exclude(pk=self.pk)

        for existing in overlapping_schedules:
            if self.start_time < existing.end_time and self.end_time > existing.start_time:
                raise ValidationError(
                    f"This schedule overlaps with an existing shift: "
                    f"{existing.start_time} - {existing.end_time}"
                )

    class Meta:
        indexes = [
            models.Index(fields=["doctor", "day_of_week"]),
        ]


class DoctorSlot(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="slots",
    )
    schedule = models.ForeignKey(
        DoctorSchedule,
        on_delete=models.SET_NULL,
        related_name="slots",
        null=True,
        blank=True,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        related_name="slot",
        null=True,
        blank=True,
    )
    exception = models.ForeignKey(
        "ScheduleException",
        on_delete=models.SET_NULL,
        related_name="slots",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "start_time"],
                name="unique_doctor_slot_start_time",
            ),
        ]
        indexes = [
            models.Index(fields=["doctor", "is_available", "start_time"]),
            models.Index(fields=["start_time"]),
        ]


class ScheduleException(models.Model):
    class ExceptionType(models.TextChoices):
        OFF = 'off', 'Day Off/Vacation'
        WORK = 'work', "One-off Working Day"

    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="exceptions")
    exception_date = models.DateField()
    exception_type = models.CharField(
        choices=ExceptionType.choices, max_length=50)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    slot_duration_minutes = models.IntegerField(default=30)
    buffer_time_minutes = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.exception_type == self.ExceptionType.WORK:
            if not self.start_time or not self.end_time:
                raise ValidationError({
                    "start_time": "Working exceptions must have start and end times."
                })
            if self.start_time >= self.end_time:
                raise ValidationError(
                    "Start time must be earlier than end time.")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "exception_date"],
                name="unique_doctor_exception_date",
            )
        ]
