import os
import django
import random
from datetime import date, timedelta, time
from faker import Faker

# Setup Django before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, DoctorProfile, PatientProfile
from scheduling.models import DoctorSchedule, DoctorSlot
from appointments.models import Appointment
from scheduling.services.slot_generation_service import SlotGenerationService

def seed_everything():
    fake = Faker()
    
    print("Seeding doctors...")
    for _ in range(5):
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password="password123",
                role='doctor',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            DoctorProfile.objects.create(user=user, specialization=fake.job())

    print("Seeding patients...")
    for _ in range(10):
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password="password123",
                role='patient',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            PatientProfile.objects.create(
                user=user,
                date_of_birth=fake.date_of_birth(minimum_age=18),
                blood_type=random.choice(['A+', 'B+', 'O-', 'AB+']),
                gender=random.choice(['male', 'female'])
            )

    doctors = DoctorProfile.objects.all()
    patients = PatientProfile.objects.all()
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

    print("Seeding weekly schedules...")
    for doctor in doctors:
        if not doctor.schedules.exists():
            working_days = random.sample(days, 3)
            for day in working_days:
                DoctorSchedule.objects.create(
                    doctor=doctor,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    slot_duration_minutes=30,
                    buffer_time_minutes=5
                )

    print("Generating slots for the next 7 days...")
    today = date.today()
    for i in range(7):
        current_date = today + timedelta(days=i)
        for doctor in doctors:
            SlotGenerationService.generate_slots_for_date(doctor, current_date)

    print("Booking some appointments...")
    for _ in range(15):
        slot = DoctorSlot.objects.filter(
            is_available=True, 
            appointment__isnull=True
        ).order_by("?").first()
        
        if slot and patients.exists():
            patient = random.choice(patients)
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=slot.doctor,
                start_time=slot.start_time,
                end_time=slot.end_time,
                status=Appointment.Status.CONFIRMED
            )
            slot.appointment = appointment
            slot.is_available = False
            slot.save()

    print("\n✅ Seeding Complete!")
    print(f"Created: {doctors.count()} Doctors, {patients.count()} Patients")
    print(f"Total Slots: {DoctorSlot.objects.count()}, Appointments: {Appointment.objects.count()}")

if __name__ == "__main__":
    seed_everything()
