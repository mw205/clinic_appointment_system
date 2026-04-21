from django.core.validators import MinValueValidator
from django.db import models

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
