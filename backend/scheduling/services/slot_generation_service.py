from datetime import datetime, time, timedelta

from django.utils.timezone import make_aware

from accounts.models import DoctorProfile
from scheduling.models import DoctorSchedule, ScheduleException


class SlotGenerationService:
    @classmethod
    def generate_slots_for_date(cls, doctor: DoctorProfile, target_date) -> list[dict]:
        exception = ScheduleException.objects.filter(
            doctor=doctor, exception_date=target_date
        ).first()
        if exception:
            if exception.exception_type == ScheduleException.ExceptionType.OFF:
                return []
            sources = [exception]
        else:
            day_name = target_date.strftime("%A").lower()
            sources = DoctorSchedule.objects.filter(doctor=doctor, day_of_week=day_name)
        slots = []
        for source in sources:
            current_dt = make_aware(datetime.combine(target_date, source.start_time))
            end_dt = make_aware(datetime.combine(target_date, source.end_time))
            duration = timedelta(minutes=source.slot_duration_minutes)
            buffer = timedelta(minutes=source.buffer_time_minutes)
            while current_dt + duration <= end_dt:
                slots.append(
                    {"start_time": current_dt, "end_time": current_dt + duration}
                )
                current_dt = current_dt + duration + buffer
        return slots
