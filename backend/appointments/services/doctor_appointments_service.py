from appointments.models import Appointment

def get_doctor_appointments(doctor):
    return Appointment.objects.filter(doctor=doctor).order_by("check_in_time")

def get_doctor_daily_queue(doctor):
    return (Appointment.objects.filter(doctor=doctor)
            .exclude(status__in=[Appointment.Status.REQUESTED, Appointment.Status.CANCELLED]))