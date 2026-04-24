from django.utils import timezone

from accounts.models import DoctorProfile
from appointments.models import Appointment
from scheduling.services.slot_generation_service import SlotGenerationService


class AvailabilityService:
    @classmethod
    def get_available_slots(cls, doctor: DoctorProfile, target_date):
        potential_slots = SlotGenerationService.generate_slots_for_date(
            doctor=doctor, target_date=target_date
        )
        booked_appointments = Appointment.objects.filter(
            doctor=doctor, start_time__date=target_date
        ).exclude(status="cancelled")

        now = timezone.now()
        available_slots = []
        for slot in potential_slots:
            if slot["start_time"] <= now:
                continue
            is_taken = any(
                app.start_time < slot["end_time"] and app.end_time > slot["start_time"]
                for app in booked_appointments
            )
            if not is_taken:
                available_slots.append(slot)
        return available_slots
