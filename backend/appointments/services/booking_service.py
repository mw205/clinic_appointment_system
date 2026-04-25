from datetime import datetime, timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from accounts.models import DoctorProfile, PatientProfile
from appointments.exceptions import (
    AppointmentCancellationError,
    BookingBadRequestError,
    BufferTimeViolationError,
    DoctorBookedError,
    PatientOverlapError,
    SlotUnavailableError,
)
from appointments.models import Appointment
from scheduling.models import DAY_OF_WEEK_CHOICES, DoctorSchedule


DEFAULT_BUFFER_TIME_MINUTES = 5
DEFAULT_CANCELLATION_WINDOW_HOURS = 2
DAY_NAME_BY_WEEKDAY = {}

for index, choice in enumerate(DAY_OF_WEEK_CHOICES):
    day_name = choice[0]
    DAY_NAME_BY_WEEKDAY[index] = day_name


def create_appointment(patient, doctor, start_time):
    patient_profile = resolve_patient_profile(patient)
    doctor_profile = resolve_doctor_profile(doctor)
    normalized_start_time = normalize_start_time(start_time)

    schedule = get_bookable_schedule(doctor_profile, normalized_start_time)
    _, normalized_end_time = get_slot_window(schedule, normalized_start_time)
    buffer_minutes = resolve_buffer_minutes(schedule)

    with transaction.atomic():
        locked_schedule = get_bookable_schedule(
            doctor_profile,
            normalized_start_time,
            for_update=True,
        )
        _, normalized_end_time = get_slot_window(locked_schedule, normalized_start_time)

        check_doctor_conflict(doctor_profile, normalized_start_time, normalized_end_time)
        check_patient_overlap(patient_profile, normalized_start_time, normalized_end_time)
        apply_buffer_time_rules(
            doctor_profile,
            normalized_start_time,
            normalized_end_time,
            buffer_minutes,
        )

        try:
            return Appointment.objects.create(
                patient=patient_profile,
                doctor=doctor_profile,
                start_time=normalized_start_time,
                end_time=normalized_end_time,
            )
        except IntegrityError as exc:
            raise DoctorBookedError("Doctor already booked for this slot.") from exc


def cancel_appointment(appointment, cancelled_by):
    if cancelled_by is None:
        raise AppointmentCancellationError("A cancelling user is required.")

    if appointment.status == Appointment.Status.COMPLETED:
        raise AppointmentCancellationError("Completed appointments cannot be cancelled.")
    if appointment.status == Appointment.Status.CANCELLED:
        raise AppointmentCancellationError("Appointment is already cancelled.")

    cancellation_window_hours = int(
        getattr(
            settings,
            "CANCELLATION_WINDOW_HOURS",
            DEFAULT_CANCELLATION_WINDOW_HOURS,
        )
    )
    if cancellation_window_hours < 0:
        raise AppointmentCancellationError(
            "Cancellation window hours must be zero or a positive integer."
        )

    appointment_start_time = localize_datetime(appointment.start_time)
    if timezone.now() >= appointment_start_time:
        raise AppointmentCancellationError("Past appointments cannot be cancelled.")

    cancellation_deadline = appointment_start_time - timedelta(
        hours=cancellation_window_hours
    )
    if timezone.now() >= cancellation_deadline:
        raise AppointmentCancellationError(
            "Appointment cannot be cancelled within "
            f"{cancellation_window_hours} hours of start time."
        )

    appointment.status = Appointment.Status.CANCELLED
    appointment.save(update_fields=["status"])
    return appointment


def resolve_patient_profile(patient):
    if patient is None:
        raise BookingBadRequestError("Patient is required.")
    if isinstance(patient, PatientProfile):
        if getattr(patient, "pk", None) is None:
            raise BookingBadRequestError("Patient profile must be saved.")
        return patient

    if getattr(patient, "pk", None) is None:
        raise BookingBadRequestError("Patient must be a saved profile or user.")

    patient_profile = PatientProfile.objects.filter(user=patient).first()
    if patient_profile is None:
        raise BookingBadRequestError("No patient profile found for this user.")
    return patient_profile


def resolve_doctor_profile(doctor):
    if doctor is None:
        raise BookingBadRequestError("Doctor is required.")
    if isinstance(doctor, DoctorProfile):
        if getattr(doctor, "pk", None) is None:
            raise BookingBadRequestError("Doctor profile must be saved.")
        return doctor

    if getattr(doctor, "pk", None) is None:
        raise BookingBadRequestError("Doctor must be a saved profile or user.")

    doctor_profile = DoctorProfile.objects.filter(user=doctor).first()
    if doctor_profile is None:
        raise BookingBadRequestError("No doctor profile found for this user.")
    return doctor_profile


def normalize_start_time(start_time):
    if start_time is None:
        raise BookingBadRequestError("Start time is required.")
    if not isinstance(start_time, datetime):
        raise BookingBadRequestError("Start time must be a datetime.")

    start_time = localize_datetime(start_time)
    now_value = timezone.now()

    if start_time <= now_value:
        raise BookingBadRequestError("Start time must be in the future.")

    return start_time


def get_bookable_schedule(doctor_profile, start_time, for_update=False):
    schedules = DoctorSchedule.objects
    if for_update:
        schedules = schedules.select_for_update()

    localized_start_time = localize_datetime(start_time)
    weekday_name = DAY_NAME_BY_WEEKDAY[localized_start_time.weekday()]
    appointment_start_time = localized_start_time.time()

    schedule = (
        schedules.filter(
            doctor=doctor_profile,
            day_of_week=weekday_name,
            start_time__lte=appointment_start_time,
            end_time__gt=appointment_start_time,
        ).first()
    )
    if schedule is None:
        raise SlotUnavailableError("Requested slot does not exist in scheduling.")
    get_slot_window(schedule, start_time)
    return schedule


def check_doctor_conflict(
    doctor_profile,
    start_time,
    end_time,
    excluded_appointment=None,
):
    appointments = Appointment.objects.filter(doctor=doctor_profile)
    if excluded_appointment is not None:
        appointments = appointments.exclude(pk=excluded_appointment.pk)

    if has_appointment_overlap(
        appointments,
        start_time,
        end_time,
    ):
        raise DoctorBookedError("Doctor already booked for this slot.")


def check_patient_overlap(
    patient_profile,
    start_time,
    end_time,
    excluded_appointment=None,
):
    appointments = Appointment.objects.filter(patient=patient_profile)
    if excluded_appointment is not None:
        appointments = appointments.exclude(pk=excluded_appointment.pk)

    if has_appointment_overlap(
        appointments,
        start_time,
        end_time,
    ):
        raise PatientOverlapError("Patient already has an overlapping appointment.")


def apply_buffer_time_rules(
    doctor_profile,
    start_time,
    end_time,
    buffer_minutes,
    excluded_appointment=None,
):
    if buffer_minutes <= 0:
        return

    window_start = start_time - timedelta(minutes=buffer_minutes)
    window_end = end_time + timedelta(minutes=buffer_minutes)
    appointments = Appointment.objects.filter(doctor=doctor_profile)
    if excluded_appointment is not None:
        appointments = appointments.exclude(pk=excluded_appointment.pk)

    if has_appointment_overlap(
        appointments,
        window_start,
        window_end,
    ):
        raise BufferTimeViolationError(
            f"Doctor buffer time of {buffer_minutes} minutes is not respected."
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


def resolve_buffer_minutes(schedule):
    if schedule.buffer_time_minutes is not None:
        buffer_minutes = schedule.buffer_time_minutes
    else:
        buffer_minutes = int(
            getattr(
                settings,
                "APPOINTMENTS_DEFAULT_BUFFER_TIME_MINUTES",
                DEFAULT_BUFFER_TIME_MINUTES,
            )
        )

    if buffer_minutes < 0:
        raise BookingBadRequestError("Buffer time must be zero or a positive integer.")
    return buffer_minutes


def get_slot_window(schedule, start_time, duration=None):
    localized_start_time = localize_datetime(start_time)
    slot_duration_minutes = schedule.slot_duration_minutes
    if slot_duration_minutes <= 0:
        raise SlotUnavailableError("Schedule slot duration must be a positive integer.")

    buffer_minutes = resolve_buffer_minutes(schedule)
    slot_step_minutes = slot_duration_minutes + buffer_minutes
    appointment_duration = duration or timedelta(minutes=slot_duration_minutes)
    if appointment_duration.total_seconds() <= 0:
        raise SlotUnavailableError("Appointment duration must be positive.")

    end_time = localized_start_time + appointment_duration
    schedule_end_time = combine_with_time(localized_start_time, schedule.end_time)
    if end_time > schedule_end_time:
        raise SlotUnavailableError("Requested slot extends beyond the doctor's schedule.")
    schedule_start_time = combine_with_time(localized_start_time, schedule.start_time)

    if localized_start_time < schedule_start_time or localized_start_time >= schedule_end_time:
        raise SlotUnavailableError("Requested slot does not exist in scheduling.")

    offset_seconds = int((localized_start_time - schedule_start_time).total_seconds())
    if offset_seconds % (slot_step_minutes * 60) != 0:
        raise BookingBadRequestError(
            "Start time must align with the doctor's slot duration and buffer time."
        )

    return localized_start_time, end_time


def localize_datetime(value):
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return timezone.localtime(value)


def combine_with_time(start_time, time_value):
    return datetime.combine(
        start_time.date(),
        time_value,
        tzinfo=start_time.tzinfo,
    )
