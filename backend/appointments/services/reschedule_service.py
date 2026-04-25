from datetime import datetime

from django.db import transaction
from django.utils import timezone

from appointments.exceptions import BookingBadRequestError
from appointments.models import RescheduleHistory


def reschedule_appointment(appointment, new_start_time, changed_by, reason=""):
    if appointment is None:
        raise BookingBadRequestError("Appointment is required.")
    if getattr(appointment, "pk", None) is None:
        raise BookingBadRequestError("Appointment must be saved before rescheduling.")
    if changed_by is None or getattr(changed_by, "pk", None) is None:
        raise BookingBadRequestError("A saved user is required to reschedule.")

    normalized_start_time = normalize_start_time(new_start_time)
    duration = appointment.end_time - appointment.start_time
    if duration.total_seconds() <= 0:
        raise BookingBadRequestError("Appointment duration must be positive.")

    old_start_time = appointment.start_time
    appointment.start_time = normalized_start_time
    appointment.end_time = normalized_start_time + duration

    with transaction.atomic():
        appointment.save(update_fields=["start_time", "end_time"])
        RescheduleHistory.objects.create(
            appointment=appointment,
            old_start_time=old_start_time,
            new_start_time=appointment.start_time,
            changed_by=changed_by,
            reason=reason or "",
        )

    return appointment


def normalize_start_time(start_time):
    if start_time is None:
        raise BookingBadRequestError("New start time is required.")
    if not isinstance(start_time, datetime):
        raise BookingBadRequestError("New start time must be a datetime.")

    if timezone.is_naive(start_time):
        start_time = timezone.make_aware(start_time, timezone.get_current_timezone())

    return timezone.localtime(start_time)
