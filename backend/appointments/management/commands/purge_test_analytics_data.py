from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q

from accounts.models import DoctorProfile, PatientProfile, User
from appointments.models import Appointment
from consultations.models import ConsultationRecord


TEST_USERNAME_PREFIX = "testseed_"


class Command(BaseCommand):
    help = "Delete seeded test-only appointments, consultations, and disposable test users."

    @transaction.atomic
    def handle(self, *args, **options):
        consultations_deleted = 0
        appointments_deleted = 0

        if self._model_has_field(ConsultationRecord, "is_test_data"):
            consultations_deleted, _ = ConsultationRecord.objects.filter(is_test_data=True).delete()
        else:
            self.stdout.write(
                self.style.WARNING(
                    "ConsultationRecord.is_test_data not found. Skipping consultation purge by flag."
                )
            )

        if self._model_has_field(Appointment, "is_test_data"):
            appointments_deleted, _ = Appointment.objects.filter(is_test_data=True).delete()
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Appointment.is_test_data not found. Skipping appointment purge by flag."
                )
            )

        doctor_users_deleted = self._delete_unused_test_doctors()
        patient_users_deleted = self._delete_unused_test_patients()

        self.stdout.write(self.style.SUCCESS("Test analytics data purge completed."))
        self.stdout.write(f"Deleted consultation rows: {consultations_deleted}")
        self.stdout.write(f"Deleted appointment rows: {appointments_deleted}")
        self.stdout.write(f"Deleted disposable doctor users: {doctor_users_deleted}")
        self.stdout.write(f"Deleted disposable patient users: {patient_users_deleted}")

    def _model_has_field(self, model, field_name):
        try:
            model._meta.get_field(field_name)
            return True
        except Exception:
            return False

    def _delete_unused_test_doctors(self):
        doctors = (
            DoctorProfile.objects.filter(user__username__startswith=f"{TEST_USERNAME_PREFIX}doctor_")
            .annotate(
                total_appointments=Count("doctor_appointments"),
                total_consultations=Count("written_consultation"),
            )
            .filter(total_appointments=0, total_consultations=0)
            .select_related("user")
        )
        user_ids = [doctor.user_id for doctor in doctors]
        if user_ids:
            DoctorProfile.objects.filter(user_id__in=user_ids).delete()
        return User.objects.filter(id__in=user_ids).delete()[0]

    def _delete_unused_test_patients(self):
        annotations = {
            "total_appointments": Count("patient_appointments"),
        }
        if self._model_has_field(Appointment, "is_test_data"):
            annotations["non_test_appointments"] = Count(
                "patient_appointments",
                filter=Q(patient_appointments__is_test_data=False),
            )

        patients = PatientProfile.objects.filter(
            user__username__startswith=f"{TEST_USERNAME_PREFIX}patient_"
        ).annotate(**annotations)

        if "non_test_appointments" in annotations:
            patients = patients.filter(non_test_appointments=0, total_appointments=0)
        else:
            patients = patients.filter(total_appointments=0)

        patients = patients.select_related("user")
        user_ids = [patient.user_id for patient in patients]
        if user_ids:
            PatientProfile.objects.filter(user_id__in=user_ids).delete()
        return User.objects.filter(id__in=user_ids).delete()[0]
