from django.conf import settings
from django.db import models

from accounts.models import DoctorProfile, PatientProfile


class Appointment(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        CHECKED_IN = "checked_in", "Checked In"
        COMPLETED = "completed", "Completed"
        NO_SHOW = "no_show", "No Show"

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    check_in_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "start_time"],
                name="unique_doctor_start_time",
            )
        ]
        indexes = [
            models.Index(fields=["start_time"]),
            models.Index(fields=["patient", "start_time"]),
            models.Index(fields=["status", "start_time"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.get_status_display()} appointment "
            f"({self.start_time:%Y-%m-%d %H:%M} - {self.end_time:%H:%M})"
        )


class RescheduleHistory(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="reschedule_history",
    )
    old_start_time = models.DateTimeField()
    new_start_time = models.DateTimeField()
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointment_reschedule_changes",
    )
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["appointment", "timestamp"]),
            models.Index(fields=["changed_by", "timestamp"]),
        ]

    def __str__(self) -> str:
        return (
            f"Reschedule for appointment #{self.appointment_id}: "
            f"{self.old_start_time:%Y-%m-%d %H:%M} -> "
            f"{self.new_start_time:%Y-%m-%d %H:%M}"
        )
