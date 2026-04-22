from appointments.models import Appointment


def get_doctor_queue(doctor, date):
    return Appointment.objects.filter(
        doctor=doctor,
        start_time__date=date,
        status=Appointment.Status.CONFIRMED
    ).order_by("check_in_time")
