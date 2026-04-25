from django.db import IntegrityError, transaction
from django.utils import timezone

from appointments.exceptions import (
    BookingBadRequestError,
    DoctorBookedError,
)
from appointments.models import Appointment, RescheduleHistory
from appointments.services.booking_service import (
    apply_buffer_time_rules,
    check_doctor_conflict,
    check_patient_overlap,
    get_bookable_schedule,
    get_slot_window,
    normalize_start_time,
    resolve_buffer_minutes,
)


BLOCKED_RESCHEDULE_STATUSES = [
    Appointment.Status.CANCELLED,
    Appointment.Status.COMPLETED,
    Appointment.Status.NO_SHOW,
]


def reschedule_appointment(appointment, new_start_time, changed_by, reason=""):
    validate_reschedule_request(appointment, changed_by)
    normalized_start_time = normalize_start_time(new_start_time)

    with transaction.atomic():
        appointment = Appointment.objects.select_for_update().get(pk=appointment.pk)
        validate_reschedule_status(appointment)
        validate_new_start_time_is_different(appointment, normalized_start_time)

        duration = get_existing_duration(appointment)
        normalized_end_time = normalized_start_time + duration
        schedule = get_bookable_schedule(
            appointment.doctor,
            normalized_start_time,
            for_update=True,
        )
        _, normalized_end_time = get_slot_window(
            schedule,
            normalized_start_time,
            duration=duration,
        )
        buffer_minutes = resolve_buffer_minutes(schedule)

        check_doctor_conflict(
            appointment.doctor,
            normalized_start_time,
            normalized_end_time,
            excluded_appointment=appointment,
        )
        check_patient_overlap(
            appointment.patient,
            normalized_start_time,
            normalized_end_time,
            excluded_appointment=appointment,
        )
        apply_buffer_time_rules(
            appointment.doctor,
            normalized_start_time,
            normalized_end_time,
            buffer_minutes,
            excluded_appointment=appointment,
        )

        old_start_time = appointment.start_time
        appointment.start_time = normalized_start_time
        appointment.end_time = normalized_end_time

        try:
            appointment.save(update_fields=["start_time", "end_time"])
        except IntegrityError as exc:
            raise DoctorBookedError("Doctor already booked for this slot.") from exc

        RescheduleHistory.objects.create(
            appointment=appointment,
            old_start_time=old_start_time,
            new_start_time=appointment.start_time,
            changed_by=changed_by,
            reason=reason or "",
        )

    return appointment


def validate_reschedule_request(appointment, changed_by):
    if appointment is None:
        raise BookingBadRequestError("Appointment is required.")
    if getattr(appointment, "pk", None) is None:
        raise BookingBadRequestError("Appointment must be saved before rescheduling.")
    if changed_by is None or getattr(changed_by, "pk", None) is None:
        raise BookingBadRequestError("A saved user is required to reschedule.")


def validate_reschedule_status(appointment):
    if appointment.status in BLOCKED_RESCHEDULE_STATUSES:
        raise BookingBadRequestError(
            "Cancelled, completed, and no-show appointments cannot be rescheduled."
        )


def validate_new_start_time_is_different(appointment, new_start_time):
    current_start_time = timezone.localtime(appointment.start_time)
    if current_start_time == timezone.localtime(new_start_time):
        raise BookingBadRequestError(
            "New start time must be different from the current start time."
        )


def get_existing_duration(appointment):
    duration = appointment.end_time - appointment.start_time
    if duration.total_seconds() <= 0:
        raise BookingBadRequestError("Appointment duration must be positive.")
    return duration
