from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from accounts.models import DoctorProfile, PatientProfile
from appointments.models import Appointment
from scheduling.models import DoctorSchedule, DoctorSlot


DEFAULT_APPOINTMENT_DURATION_MINUTES = 30
DEFAULT_BUFFER_TIME_MINUTES = 5


def create_appointment(*, patient, doctor, start_time):
    patient_profile = _resolve_patient_profile(patient)
    doctor_profile = _resolve_doctor_profile(doctor)
    normalized_start_time = _normalize_start_time(start_time)

    schedule = _get_matching_schedule(
        doctor_profile=doctor_profile,
        start_time=normalized_start_time,
    )
    duration = _resolve_appointment_duration(schedule=schedule)
    end_time = normalized_start_time + duration

    _validate_within_doctor_schedule(
        schedule=schedule,
        start_time=normalized_start_time,
        end_time=end_time,
    )

    with transaction.atomic():
        _ensure_slots_generated_for_start_time(
            doctor_profile=doctor_profile,
            schedule=schedule,
            start_time=normalized_start_time,
            duration=duration,
        )
        slot = _lock_available_slot(
            doctor_profile=doctor_profile,
            start_time=normalized_start_time,
            end_time=end_time,
        )
        if slot is None:
            raise ValidationError(
                {"start_time": "No available slot found for this doctor at the requested time."}
            )

        _validate_no_overlapping_appointments(
            patient=patient_profile,
            doctor=doctor_profile,
            start_time=normalized_start_time,
            end_time=end_time,
        )

        try:
            appointment = Appointment.objects.create(
                patient=patient_profile,
                doctor=doctor_profile,
                start_time=normalized_start_time,
                end_time=end_time,
            )
        except IntegrityError as exc:
            raise ValidationError(
                {"start_time": "This doctor already has an appointment at this time."}
            ) from exc

        _mark_slot_as_booked(slot=slot, appointment=appointment)
        return appointment


def _resolve_patient_profile(patient):
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


def _resolve_doctor_profile(doctor):
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


def _normalize_start_time(start_time):
    if start_time is None:
        raise ValidationError({"start_time": "Start time is required."})
    if not isinstance(start_time, datetime):
        raise ValidationError({"start_time": "Start time must be a datetime."})

    if timezone.is_naive(start_time):
        start_time = timezone.make_aware(start_time, timezone.get_current_timezone())

    if start_time <= timezone.now():
        raise ValidationError({"start_time": "Start time must be in the future."})

    return start_time


def _resolve_appointment_duration(*, schedule):
    if schedule is None:
        minutes = _get_default_appointment_duration_minutes()
        return timedelta(minutes=minutes)

    slot_duration_minutes = int(schedule.slot_duration_minutes)
    if slot_duration_minutes <= 0:
        raise ValidationError(
            {"start_time": "Doctor schedule slot duration must be a positive value."}
        )
    return timedelta(minutes=slot_duration_minutes)


def _validate_within_doctor_schedule(*, schedule, start_time, end_time):
    if schedule is None:
        return

    schedule_start = timezone.localtime(schedule.start_time)
    schedule_end = timezone.localtime(schedule.end_time)
    requested_start = timezone.localtime(start_time)
    requested_end = timezone.localtime(end_time)

    schedule_start_time = schedule_start.time()
    schedule_end_time = schedule_end.time()

    if not (
        schedule_start_time <= requested_start.time()
        and requested_end.time() <= schedule_end_time
    ):
        raise ValidationError(
            {"start_time": "Appointment time is outside the doctor's schedule."}
        )


def _validate_no_overlapping_appointments(*, patient, doctor, start_time, end_time):
    blocking_statuses = [
        Appointment.Status.REQUESTED,
        Appointment.Status.CONFIRMED,
        Appointment.Status.CHECKED_IN,
    ]

    doctor_overlap_exists = (
        Appointment.objects.select_for_update()
        .filter(
            doctor=doctor,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=blocking_statuses,
        )
        .exists()
    )
    if doctor_overlap_exists:
        raise ValidationError(
            {"start_time": "Doctor already has another appointment in this time range."}
        )

    patient_overlap_exists = (
        Appointment.objects.select_for_update()
        .filter(
            patient=patient,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=blocking_statuses,
        )
        .exists()
    )
    if patient_overlap_exists:
        raise ValidationError(
            {"start_time": "Patient already has another appointment in this time range."}
        )


def _get_matching_schedule(*, doctor_profile, start_time):
    day_of_week = timezone.localtime(start_time).strftime("%A").lower()
    return (
        DoctorSchedule.objects.filter(
            doctor=doctor_profile,
            day_of_week=day_of_week,
            start_time__time__lte=start_time.time(),
            end_time__time__gt=start_time.time(),
        )
        .order_by("start_time")
        .first()
    )


def _ensure_slots_generated_for_start_time(*, doctor_profile, schedule, start_time, duration):
    slot_exists = DoctorSlot.objects.filter(
        doctor=doctor_profile,
        start_time=start_time,
    ).exists()
    if slot_exists:
        return

    if schedule is None:
        return

    _generate_daily_slots_for_schedule(
        doctor_profile=doctor_profile,
        schedule=schedule,
        target_start_time=start_time,
    )


def _generate_daily_slots_for_schedule(*, doctor_profile, schedule, target_start_time):
    target_local = timezone.localtime(target_start_time)
    schedule_start_local = timezone.localtime(schedule.start_time)
    schedule_end_local = timezone.localtime(schedule.end_time)
    timezone_obj = timezone.get_current_timezone()

    window_start = timezone.make_aware(
        datetime.combine(target_local.date(), schedule_start_local.time()),
        timezone_obj,
    )
    window_end = timezone.make_aware(
        datetime.combine(target_local.date(), schedule_end_local.time()),
        timezone_obj,
    )

    duration = timedelta(minutes=int(schedule.slot_duration_minutes))
    if duration.total_seconds() <= 0:
        raise ValidationError(
            {"start_time": "Doctor schedule slot duration must be a positive value."}
        )

    buffer_minutes = _resolve_buffer_minutes(schedule)
    step = duration + timedelta(minutes=buffer_minutes)
    if step.total_seconds() <= 0:
        raise ValidationError({"start_time": "Slot step duration must be positive."})

    cursor = window_start
    while cursor + duration <= window_end:
        DoctorSlot.objects.get_or_create(
            doctor=doctor_profile,
            start_time=cursor,
            defaults={
                "schedule": schedule,
                "end_time": cursor + duration,
                "is_available": True,
            },
        )
        cursor += step


def _lock_available_slot(*, doctor_profile, start_time, end_time):
    return (
        DoctorSlot.objects.select_for_update()
        .filter(
            doctor=doctor_profile,
            start_time=start_time,
            end_time=end_time,
            is_available=True,
            appointment__isnull=True,
        )
        .first()
    )


def _mark_slot_as_booked(*, slot, appointment):
    slot.is_available = False
    slot.appointment = appointment
    slot.save(update_fields=["is_available", "appointment", "updated_at"])


def _resolve_buffer_minutes(schedule):
    if schedule is None:
        return DEFAULT_BUFFER_TIME_MINUTES

    buffer_minutes = int(
        getattr(schedule, "buffer_time_minutes", DEFAULT_BUFFER_TIME_MINUTES)
    )
    if buffer_minutes < 0:
        raise ValidationError(
            {"start_time": "Doctor schedule buffer time must be zero or positive."}
        )
    return buffer_minutes


def _get_default_appointment_duration_minutes():
    minutes = int(
        getattr(
            settings,
            "APPOINTMENTS_DEFAULT_DURATION_MINUTES",
            DEFAULT_APPOINTMENT_DURATION_MINUTES,
        )
    )
    if minutes <= 0:
        raise ValidationError(
            {
                "start_time": (
                    "APPOINTMENTS_DEFAULT_DURATION_MINUTES must be a positive integer."
                )
            }
        )
    return minutes
