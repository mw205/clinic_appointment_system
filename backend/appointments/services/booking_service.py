from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from accounts.models import DoctorProfile, PatientProfile
from appointments.models import Appointment
from scheduling.models import DoctorSlot


DEFAULT_BUFFER_TIME_MINUTES = 5


class SlotUnavailableError(ValidationError):
    pass


class DoctorBookedError(ValidationError):
    pass


class PatientOverlapError(ValidationError):
    pass


class BufferTimeViolationError(ValidationError):
    pass


def create_appointment(patient, doctor, start_time):
    patient_profile = resolve_patient_profile(patient)
    doctor_profile = resolve_doctor_profile(doctor)
    normalized_start_time = normalize_start_time(start_time)

    slot = validate_slot_availability(doctor_profile, normalized_start_time)
    normalized_end_time = normalize_slot_end_time(slot.end_time)
    buffer_minutes = resolve_buffer_minutes(slot)

    with transaction.atomic():
        locked_slot = lock_available_slot(doctor_profile, normalized_start_time)
        if locked_slot is None:
            raise SlotUnavailableError(
                {"start_time": "Requested slot is no longer available."}
            )

        normalized_end_time = normalize_slot_end_time(locked_slot.end_time)

        check_doctor_conflict(doctor_profile, normalized_start_time, normalized_end_time)
        check_patient_overlap(patient_profile, normalized_start_time, normalized_end_time)
        apply_buffer_time_rules(
            doctor_profile,
            normalized_start_time,
            normalized_end_time,
            buffer_minutes,
        )

        try:
            appointment = Appointment.objects.create(
                patient=patient_profile,
                doctor=doctor_profile,
                start_time=normalized_start_time,
                end_time=normalized_end_time,
            )
            locked_slot.is_available = False
            locked_slot.appointment = appointment
            locked_slot.save(update_fields=["is_available", "appointment", "updated_at"])
        except IntegrityError as exc:
            raise DoctorBookedError(
                {"start_time": "Booking conflict detected. Please try a different slot."}
            ) from exc

        return appointment


def resolve_patient_profile(patient):
    if patient is None:
        raise ValidationError({"patient": "Patient is required."})
    if isinstance(patient, PatientProfile):
        if getattr(patient, "pk", None) is None:
            raise ValidationError({"patient": "Patient profile must be saved."})
        return patient

    if getattr(patient, "pk", None) is None:
        raise ValidationError({"patient": "Patient must be a saved profile or user."})

    patient_profile = PatientProfile.objects.filter(user=patient).first()
    if patient_profile is None:
        raise ValidationError({"patient": "No patient profile found for this user."})
    return patient_profile


def resolve_doctor_profile(doctor):
    if doctor is None:
        raise ValidationError({"doctor": "Doctor is required."})
    if isinstance(doctor, DoctorProfile):
        if getattr(doctor, "pk", None) is None:
            raise ValidationError({"doctor": "Doctor profile must be saved."})
        return doctor

    if getattr(doctor, "pk", None) is None:
        raise ValidationError({"doctor": "Doctor must be a saved profile or user."})

    doctor_profile = DoctorProfile.objects.filter(user=doctor).first()
    if doctor_profile is None:
        raise ValidationError({"doctor": "No doctor profile found for this user."})
    return doctor_profile


def normalize_start_time(start_time):
    if start_time is None:
        raise ValidationError({"start_time": "Start time is required."})
    if not isinstance(start_time, datetime):
        raise ValidationError({"start_time": "Start time must be a datetime."})

    if start_time <= datetime.now():
        raise ValidationError({"start_time": "Start time must be in the future."})

    return start_time


def normalize_slot_end_time(end_time):
    if end_time is None:
        raise ValidationError({"start_time": "Requested slot has no end time."})
    if not isinstance(end_time, datetime):
        raise ValidationError({"start_time": "Slot end time must be a datetime."})

    return end_time


def validate_slot_availability(doctor_profile, start_time):
    slot = fetch_slot_from_scheduling(doctor_profile, start_time)
    if slot is None:
        raise SlotUnavailableError(
            {"start_time": "Requested slot does not exist in scheduling."}
        )
    if not slot.is_available:
        raise SlotUnavailableError(
            {"start_time": "Requested slot is not available."}
        )
    return slot


def fetch_slot_from_scheduling(doctor_profile, start_time):
    return (
        DoctorSlot.objects.select_related("schedule")
        .filter(
            doctor=doctor_profile,
            start_time=start_time,
        )
        .first()
    )


def lock_available_slot(doctor_profile, start_time):
    return (
        DoctorSlot.objects.select_for_update()
        .filter(
            doctor=doctor_profile,
            start_time=start_time,
            is_available=True,
            appointment__isnull=True,
        )
        .first()
    )


def check_doctor_conflict(doctor_profile, start_time, end_time):
    if has_appointment_overlap(
        Appointment.objects.filter(doctor=doctor_profile),
        start_time,
        end_time,
    ):
        raise DoctorBookedError(
            {"start_time": "Doctor is already booked at this time."}
        )


def check_patient_overlap(patient_profile, start_time, end_time):
    if has_appointment_overlap(
        Appointment.objects.filter(patient=patient_profile),
        start_time,
        end_time,
    ):
        raise PatientOverlapError(
            {"start_time": "Patient already has an overlapping appointment."}
        )


def apply_buffer_time_rules(doctor_profile, start_time, end_time, buffer_minutes):
    if buffer_minutes <= 0:
        return

    window_start = start_time - timedelta(minutes=buffer_minutes)
    window_end = end_time + timedelta(minutes=buffer_minutes)

    if has_appointment_overlap(
        Appointment.objects.filter(doctor=doctor_profile),
        window_start,
        window_end,
    ):
        raise BufferTimeViolationError(
            {
                "start_time": (
                    f"Doctor buffer time of {buffer_minutes} minutes is not respected."
                )
            }
        )

def has_appointment_overlap(queryset, start_time, end_time):
    blocking_statuses = [
        Appointment.Status.REQUESTED,
        Appointment.Status.CONFIRMED,
        Appointment.Status.CHECKED_IN,
    ]
    return (
        queryset.select_for_update()
        .filter(
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=blocking_statuses,
        )
        .exists()
    )


def resolve_buffer_minutes(slot):
    if slot.schedule.buffer_time_minutes is not None:
        buffer_minutes = int(slot.schedule.buffer_time_minutes)
    else:
        buffer_minutes = int(
            getattr(
                settings,
                "APPOINTMENTS_DEFAULT_BUFFER_TIME_MINUTES",
                DEFAULT_BUFFER_TIME_MINUTES,
            )
        )

    if buffer_minutes < 0:
        raise ValidationError(
            {"start_time": "Buffer time must be zero or a positive integer."}
        )
    return buffer_minutes
