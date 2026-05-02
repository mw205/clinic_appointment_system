from django.db import models

class ConsultationRecord(models.Model):

    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='consultation',

    )
    doctor = models.ForeignKey(
        'accounts.DoctorProfile',
        on_delete=models.PROTECT,
        related_name='written_consultation',
    )
    diagnosis = models.TextField()
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_test_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_completed(self):
        return self.completed_at is not None
    def __str__(self):
        return f"Consultation for Appointment #{self.appointment_id}"

class PrescriptionItem(models.Model):

    consultation = models.ForeignKey(
        ConsultationRecord,
        on_delete=models.CASCADE,
        related_name='prescription_items',
    )
    drug = models.CharField(max_length=255)
    dose = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return f"{self.drug} {self.dose} — Consultation #{self.consultation_id}"


class RequestedTest(models.Model):

    consultation = models.ForeignKey(
        ConsultationRecord,
        on_delete=models.CASCADE,
        related_name='requested_tests',
    )
    test_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.test_name} — Consultation #{self.consultation_id}"
