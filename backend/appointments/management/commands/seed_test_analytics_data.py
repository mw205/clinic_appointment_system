import random
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import DoctorProfile, PatientProfile, User
from appointments.models import Appointment
from consultations.models import ConsultationRecord, PrescriptionItem, RequestedTest


TEST_USERNAME_PREFIX = "testseed"
TEST_PHONE_NUMBER = "0000000000"
DOCTOR_GROUP_NAME = "Doctor"
PATIENT_GROUP_NAME = "Patient"

SPECIALIZATIONS = [
    "Cardiology",
    "Dermatology",
    "Pediatrics",
    "Neurology",
    "Internal Medicine",
    "Orthopedics",
]

DIAGNOSES = [
    "Seasonal viral infection",
    "Migraine follow-up",
    "Dermatitis flare-up",
    "Routine blood pressure review",
    "Lower back pain assessment",
    "Child wellness consultation",
]

PRESCRIPTIONS = [
    ("Paracetamol", "500 mg", "5 days", "Take after meals"),
    ("Ibuprofen", "400 mg", "3 days", "Take with water"),
    ("Cetirizine", "10 mg", "7 days", "One tablet at night"),
    ("Omeprazole", "20 mg", "14 days", "Before breakfast"),
]

REQUESTED_TESTS = [
    ("CBC", "Check for infection markers"),
    ("Lipid profile", "Routine follow-up"),
    ("Blood glucose", "Monitor fasting level"),
    ("X-ray", "Evaluate persistent pain"),
]


class Command(BaseCommand):
    help = "Seed reversible test-only appointments and consultations for dashboard verification."

    def add_arguments(self, parser):
        parser.add_argument(
            "--appointments",
            type=int,
            default=36,
            help="Number of test appointments to create. Default is 36.",
        )
        parser.add_argument(
            "--consultations",
            type=int,
            default=12,
            help=(
                "Additional number of in-progress consultations to create after all "
                "completed appointments are covered. Default is 12."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        appointment_count = max(options["appointments"], 0)
        consultation_count = max(options["consultations"], 0)

        doctors = self._get_or_create_test_doctors()
        patients = self._get_or_create_test_patients()

        appointments = self._create_test_appointments(
            doctors=doctors,
            patients=patients,
            appointment_count=appointment_count,
        )
        consultations = self._create_test_consultations(
            appointments=appointments,
            consultation_count=consultation_count,
        )

        self.stdout.write(self.style.SUCCESS("Test analytics seed completed."))
        self.stdout.write(f"Created appointments: {len(appointments)}")
        self.stdout.write(f"Created consultations: {len(consultations)}")
        self.stdout.write("All seeded records are marked with is_test_data=True.")

    def _get_or_create_test_doctors(self):
        group, _ = Group.objects.get_or_create(name=DOCTOR_GROUP_NAME)
        doctors = list(
            DoctorProfile.objects.filter(
                user__username__startswith=f"{TEST_USERNAME_PREFIX}_doctor_"
            ).select_related("user")
        )
        if doctors:
            return doctors

        doctors = []
        for index in range(1, 5):
            user = User.objects.create_user(
                username=f"{TEST_USERNAME_PREFIX}_doctor_{index}",
                password="password123",
                role="doctor",
                first_name=f"TestDoctor{index}",
                last_name="Seed",
                email=f"testdoctor{index}@example.com",
                phone_number=TEST_PHONE_NUMBER,
            )
            user.groups.add(group)
            doctors.append(
                DoctorProfile.objects.create(
                    user=user,
                    specialization=SPECIALIZATIONS[(index - 1) % len(SPECIALIZATIONS)],
                )
            )
        return doctors

    def _get_or_create_test_patients(self):
        group, _ = Group.objects.get_or_create(name=PATIENT_GROUP_NAME)
        patients = list(
            PatientProfile.objects.filter(
                user__username__startswith=f"{TEST_USERNAME_PREFIX}_patient_"
            ).select_related("user")
        )
        if patients:
            return patients

        patients = []
        for index in range(1, 9):
            user = User.objects.create_user(
                username=f"{TEST_USERNAME_PREFIX}_patient_{index}",
                password="password123",
                role="patient",
                first_name=f"TestPatient{index}",
                last_name="Seed",
                email=f"testpatient{index}@example.com",
                phone_number=TEST_PHONE_NUMBER,
            )
            user.groups.add(group)
            patients.append(
                PatientProfile.objects.create(
                    user=user,
                    date_of_birth=timezone.now().date() - timedelta(days=365 * (20 + index)),
                    blood_type=["A+", "B+", "O+", "AB+"][index % 4],
                    gender="male" if index % 2 else "female",
                )
            )
        return patients

    def _create_test_appointments(self, doctors, patients, appointment_count):
        now = timezone.now()
        created = []

        future_statuses = [
            Appointment.Status.REQUESTED,
            Appointment.Status.CONFIRMED,
        ]
        past_statuses = [
            Appointment.Status.CANCELLED,
            Appointment.Status.NO_SHOW,
            Appointment.Status.CHECKED_IN,
            Appointment.Status.COMPLETED,
        ]

        for index in range(appointment_count):
            doctor = doctors[index % len(doctors)]
            patient = patients[index % len(patients)]

            if index < appointment_count // 2:
                status = past_statuses[index % len(past_statuses)]
                start_time = (now - timedelta(days=14 - (index % 10), hours=(index % 4) + 1)).replace(
                    minute=(index % 4) * 15,
                    second=0,
                    microsecond=0,
                )
            else:
                status = future_statuses[index % len(future_statuses)]
                start_time = (now + timedelta(days=(index % 10) + 1, hours=(index % 5) + 1)).replace(
                    minute=(index % 4) * 15,
                    second=0,
                    microsecond=0,
                )

            while Appointment.objects.filter(doctor=doctor, start_time=start_time).exists():
                start_time += timedelta(minutes=30)

            end_time = start_time + timedelta(minutes=30)
            check_in_time = None
            if status in {Appointment.Status.CHECKED_IN, Appointment.Status.COMPLETED}:
                check_in_time = start_time - timedelta(minutes=10)

            created.append(
                Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    start_time=start_time,
                    end_time=end_time,
                    check_in_time=check_in_time,
                    status=status,
                    is_test_data=True,
                )
            )

        return created

    def _create_test_consultations(self, appointments, consultation_count):
        completed_appointments = [
            appointment
            for appointment in appointments
            if appointment.status == Appointment.Status.COMPLETED
        ]
        checked_in_appointments = [
            appointment
            for appointment in appointments
            if appointment.status == Appointment.Status.CHECKED_IN
        ]
        random.shuffle(checked_in_appointments)

        eligible_appointments = completed_appointments + checked_in_appointments[:consultation_count]

        created = []
        for index, appointment in enumerate(eligible_appointments):
            consultation = ConsultationRecord.objects.create(
                appointment=appointment,
                doctor=appointment.doctor,
                diagnosis=f"[TEST ONLY] {DIAGNOSES[index % len(DIAGNOSES)]}",
                notes="[TEST ONLY] Generated for AdminDashboard verification.",
                completed_at=timezone.now() - timedelta(days=index) if appointment.status == Appointment.Status.COMPLETED else None,
                is_test_data=True,
            )

            drug, dose, duration, instructions = PRESCRIPTIONS[index % len(PRESCRIPTIONS)]
            PrescriptionItem.objects.create(
                consultation=consultation,
                drug=drug,
                dose=dose,
                duration=duration,
                instructions=f"[TEST ONLY] {instructions}",
            )

            test_name, notes = REQUESTED_TESTS[index % len(REQUESTED_TESTS)]
            RequestedTest.objects.create(
                consultation=consultation,
                test_name=test_name,
                notes=f"[TEST ONLY] {notes}",
            )

            created.append(consultation)

        invalid_completed_without_consultation = Appointment.objects.filter(
            is_test_data=True,
            status=Appointment.Status.COMPLETED,
            consultation__isnull=True,
        ).count()
        if invalid_completed_without_consultation:
            raise RuntimeError(
                "Test analytics seed integrity failed: completed test appointments "
                "without consultations "
                f"({invalid_completed_without_consultation})."
            )

        return created
