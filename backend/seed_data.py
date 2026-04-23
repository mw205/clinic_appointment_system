import os
import random
from datetime import date, datetime, time, timedelta

import django
from django.utils import timezone
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from accounts.models import DoctorProfile, PatientProfile, User
from appointments.models import Appointment
from scheduling.models import DoctorSchedule


def seed_everything():
    fake = Faker()

    print("Seeding doctors...")
    for _ in range(5):
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password="password123",
                role="doctor",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            DoctorProfile.objects.create(user=user, specialization=fake.job())

    print("Seeding patients...")
    for _ in range(10):
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password="password123",
                role="patient",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            PatientProfile.objects.create(
                user=user,
                date_of_birth=fake.date_of_birth(minimum_age=18),
                blood_type=random.choice(["A+", "B+", "O-", "AB+"]),
                gender=random.choice(["male", "female"]),
            )

    doctors = DoctorProfile.objects.all()
    patients = list(PatientProfile.objects.all())
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    print("Seeding weekly schedules...")
    for doctor in doctors:
        if not doctor.schedules.exists():
            for day in random.sample(days, 3):
                DoctorSchedule.objects.create(
                    doctor=doctor,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    slot_duration_minutes=30,
                    buffer_time_minutes=5,
                )

    print("Creating some future appointments...")
    created_appointments = 0
    today = date.today()

    for doctor in doctors:
        if created_appointments >= 15 or not patients:
            break

        for schedule in doctor.schedules.all():
            appointment_start = next_schedule_start(schedule, today)
            if appointment_start is None:
                continue

            appointment_end = appointment_start + timedelta(
                minutes=schedule.slot_duration_minutes
            )
            if Appointment.objects.filter(
                doctor=doctor,
                start_time=appointment_start,
            ).exists():
                continue

            Appointment.objects.create(
                patient=random.choice(patients),
                doctor=doctor,
                start_time=appointment_start,
                end_time=appointment_end,
                status=Appointment.Status.CONFIRMED,
            )
            created_appointments += 1

            if created_appointments >= 15:
                break

    print("\nSeeding complete.")
    print(f"Created: {doctors.count()} doctors, {len(patients)} patients")
    print(f"Total schedules: {DoctorSchedule.objects.count()}")
    print(f"Total appointments: {Appointment.objects.count()}")


def next_schedule_start(schedule, start_date):
    for offset in range(14):
        current_date = start_date + timedelta(days=offset)
        if current_date.strftime("%A").lower() != schedule.day_of_week:
            continue

        naive_start = datetime.combine(current_date, schedule.start_time)
        aware_start = timezone.make_aware(
            naive_start,
            timezone.get_current_timezone(),
        )
        if aware_start > timezone.now():
            return aware_start

    return None


if __name__ == "__main__":
    seed_everything()
