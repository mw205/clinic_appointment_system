from datetime import date
from django.utils import timezone
from accounts.models import DoctorProfile
from scheduling.models import DoctorSlot
from scheduling.services.slot_generation_service import SlotGenerationService


class AvailabilityService:
    @classmethod
    def get_available_slots(cls, doctor: DoctorProfile, start_date: date, end_date: date = None):
        """Fetches bookable slots, generating them on-the-fly if missing."""
        if not end_date:
            end_date = start_date
            
        current_date = start_date
        while current_date <= end_date:
            # Lazy generation: ensure slots exist before querying
            if not DoctorSlot.objects.filter(doctor=doctor, start_time__date=current_date).exists():
                SlotGenerationService.generate_slots_for_date(doctor=doctor, date=current_date)
            current_date += timezone.timedelta(days=1)
            
        now = timezone.now()
        # Filter for future, available, and unbooked slots
        available_slots = DoctorSlot.objects.filter(
            doctor=doctor,
            start_time__date__range=[start_date, end_date],
            start_time__gt=now,
            is_available=True,
            appointment__isnull=True
        ).select_related("doctor", "schedule").order_by("start_time")
        
        return available_slots
