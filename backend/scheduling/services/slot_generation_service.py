from accounts.models import DoctorProfile
from scheduling.models import DoctorSchedule, DoctorSlot, ScheduleException
from django.utils.timezone import make_aware
from django.db import transaction
from datetime import datetime, timedelta


class SlotGenerationService:
    @classmethod
    @transaction.atomic
    def generate_slots_for_date(cls, doctor: DoctorProfile, date):
        """Generates slots based on regular schedule or overrides from exceptions."""
        exception = ScheduleException.objects.filter(
            doctor=doctor,
            exception_date=date
        ).first()
        
        if exception:
            if exception.exception_type == ScheduleException.ExceptionType.OFF:
                # Clear existing slots for vacation days
                DoctorSlot.objects.filter(doctor=doctor, start_time__date=date).delete()
                return []
            sources = [exception]
        else:
            # Match current day of week (e.g., "monday")
            day_name = date.strftime("%A").lower().strip()
            sources = doctor.schedules.filter(day_of_week=day_name)
            
        slots_to_create = []
        for source in sources:
            current_dt = make_aware(datetime.combine(date, source.start_time))
            end_dt = make_aware(datetime.combine(date, source.end_time))
            duration = timedelta(minutes=source.slot_duration_minutes)
            buffer = timedelta(minutes=source.buffer_time_minutes)
            
            # Generate slots sequentially
            while current_dt + duration <= end_dt:
                slot_end = current_dt + duration
                slots_to_create.append(
                    DoctorSlot(
                        doctor=doctor,
                        schedule=source if isinstance(source, DoctorSchedule) else None,
                        exception=source if isinstance(source, ScheduleException) else None,
                        start_time=current_dt,
                        end_time=slot_end,
                        is_available=True
                    )
                )
                current_dt = slot_end + buffer
        
        # Atomically replace old slots with new ones
        DoctorSlot.objects.filter(doctor=doctor, start_time__date=date).delete()
        return DoctorSlot.objects.bulk_create(slots_to_create)
