import os
import django

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import random
from datetime import date, datetime, time, timedelta

from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone
from faker import Faker

from accounts.models import DoctorProfile, PatientProfile, User
from appointments.models import Appointment, RescheduleHistory
from scheduling.models import DoctorSchedule, ScheduleException

fake = Faker()

USER_TYPE_TO_GROUP = {
    "admin": "Admin",
    "receptionist": "Receptionist",
    "doctor": "Doctor",
    "patient": "Patient",
}

def clean_db():
    print("🧹 Cleaning database...")
    # Delete everything except superusers
    User.objects.exclude(is_superuser=True).delete()
    print("✅ Database cleaned (Superusers preserved).")

def create_users(user_type, count):
    users = []
    group_name = USER_TYPE_TO_GROUP[user_type]
    group = Group.objects.filter(name=group_name).first()

    if group is None:
        raise RuntimeError(f"Required group '{group_name}' does not exist. Run auth group setup first.")

    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{user_type}_{fake.unique.user_name()}"
        
        user = User.objects.create_user(
            username=username,
            password="password123",
            first_name=first_name,
            last_name=last_name,
            email=fake.email(),
            phone_number=fake.phone_number()[:15],
            email_verified=True,
        )
        user.groups.add(group)
        users.append(user)
    return users

@transaction.atomic
def seed_data():
    clean_db()

    # 1. Create Admins & Receptionists
    print("👥 Creating Staff...")
    admins = create_users("admin", 2)
    receptionists = create_users("receptionist", 3)

    # 2. Create Doctors
    print("👨‍⚕️ Creating Doctors & Schedules...")
    doctor_users = create_users("doctor", 8)
    specializations = ["Cardiology", "Dermatology", "Pediatrics", "Neurology", "Internal Medicine", "Orthopedics"]
    
    doctors = []
    for user in doctor_users:
        doc = DoctorProfile.objects.create(
            user=user, 
            specialization=random.choice(specializations)
        )
        doctors.append(doc)
        
        # Create Weekly Schedules (3-5 days per week)
        working_days = random.sample(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"], k=random.randint(3, 5))
        for day in working_days:
            start_hour = random.randint(8, 10)
            end_hour = random.randint(14, 18)
            DoctorSchedule.objects.create(
                doctor=doc,
                day_of_week=day,
                start_time=time(start_hour, 0),
                end_time=time(end_hour, 0),
                slot_duration_minutes=random.choice([15, 30]),
                buffer_time_minutes=5
            )
        
        # Add a Vacation Exception for each doctor in the next month
        vacation_date = date.today() + timedelta(days=random.randint(1, 30))
        ScheduleException.objects.create(
            doctor=doc,
            exception_date=vacation_date,
            exception_type=ScheduleException.ExceptionType.OFF,
            reason="Medical Conference"
        )

    # 3. Create Patients
    print("🤒 Creating Patients...")
    patient_users = create_users("patient", 20)
    patients = []
    for user in patient_users:
        patients.append(PatientProfile.objects.create(
            user=user,
            date_of_birth=fake.date_of_birth(minimum_age=5, maximum_age=85),
            blood_type=random.choice(["A+", "B+", "O+", "O-", "A-", "AB+"]),
            gender=random.choice(["male", "female"])
        ))

    # 4. Create Appointment History (Past and Future)
    print("📅 Generating Appointments...")
    today = timezone.now()

    for _ in range(80):
        doctor = random.choice(doctors)
        patient = random.choice(patients)
        
        # Pick a random date +/- 20 days
        days_offset = random.randint(-20, 20)
        random_date = today + timedelta(days=days_offset)
        
        # Ensure we pick a time within reasonable working hours
        start_time = random_date.replace(hour=random.randint(9, 15), minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=30)

        # Basic overlap check to prevent DB errors in seeder
        if not Appointment.objects.filter(doctor=doctor, start_time=start_time).exists():
            # Determine realistic status based on date
            if start_time < today:
                status = random.choice([
                    Appointment.Status.COMPLETED, 
                    Appointment.Status.NO_SHOW, 
                    Appointment.Status.CANCELLED
                ])
            else:
                status = random.choice([
                    Appointment.Status.REQUESTED, 
                    Appointment.Status.CONFIRMED
                ])
            
            appt = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                start_time=start_time,
                end_time=end_time,
                status=status
            )

            # Randomly create some reschedule history
            if random.random() > 0.85:
                RescheduleHistory.objects.create(
                    appointment=appt,
                    old_start_time=start_time - timedelta(days=1),
                    new_start_time=start_time,
                    changed_by=random.choice(receptionists),
                    reason="Patient request via phone"
                )

    print(f"""
🚀 Seeding Complete!
-------------------------------
Database Status:
- Admins: {User.objects.filter(groups__name='Admin').distinct().count()}
- Receptionists: {User.objects.filter(groups__name='Receptionist').distinct().count()}
- Doctors: {doctors.__len__()}
- Patients: {patients.__len__()}
- Appointments: {Appointment.objects.count()}
-------------------------------
All user passwords: password123
    """)

if __name__ == "__main__":
    seed_data()
