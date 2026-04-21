from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied

from appointments.models import Appointment


@api_view(['POST'])
def confirm(request, id):
    try:
        appointment = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        raise NotFound("Appointment not found")

    if not request.user.has_perm('appointments.change_appointment') or appointment.doctor != request.user:
        raise PermissionDenied("You do not have permission")

    if appointment.status != Appointment.Status.REQUESTED:
        return Response({"error": "Appointment already processed"}, status=400)

    appointment.status = Appointment.Status.CONFIRMED
    appointment.save()

    return Response({"message": "Appointment confirmed"})

def cancel(request, id):
    try:
        appointment = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        raise NotFound("Appointment not found")

    if not request.user.has_perm('appointments.change_appointment') or appointment.patient != request.user:
        raise PermissionDenied("You do not have permission")

    if appointment.status == Appointment.Status.COMPLETED:
        return Response({"error": "Appointment already completed"}, status=400)
    appointment.status = Appointment.Status.CANCELLED
    appointment.save()

    return Response({"message": "Appointment cancelled"})