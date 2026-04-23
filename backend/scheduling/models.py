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
