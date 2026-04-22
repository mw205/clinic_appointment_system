from django.urls import path

from .views import (
    AppointmentListCreateAPIView,
    AppointmentRetrieveAPIView,
    cancel,
    check_in,
    confirm,
    doctor_queue,
)


urlpatterns = [
    path("", AppointmentListCreateAPIView.as_view(), name="appointment_list_create"),
    path("<int:pk>/", AppointmentRetrieveAPIView.as_view(), name="appointment_detail"),
    path("doctor/queue/", doctor_queue, name="doctor_queue"),
    path("<int:id>/confirm/", confirm, name="appointment_confirm"),
    path("<int:id>/cancel/", cancel, name="appointment_cancel"),
    path("<int:id>/check-in/", check_in, name="appointment_check_in"),
]
