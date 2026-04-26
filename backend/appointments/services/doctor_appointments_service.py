from appointments.models import Appointment

def get_doctor_appointments(doctor):
    return Appointment.objects.filter(doctor=doctor).order_by("check_in_time")
