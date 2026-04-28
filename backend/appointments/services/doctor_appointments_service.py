from appointments.models import Appointment

def get_doctor_appointments(doctor):
    return Appointment.objects.filter(doctor=doctor).order_by("check_in_time")

def get_doctor_daily_queue(doctor):
    return Appointment.objects.filter(doctor=doctor, status__in=[Appointment.Status.CONFIRMED, Appointment.Status.CHECKED_IN])