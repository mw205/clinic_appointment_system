from django.urls import path
from .views import AppointmentBookingCreateAPIView, cancel, confirm


urlpatterns = [
    path("", AppointmentBookingCreateAPIView.as_view(), name="appointment_book"),
    path('<int:id>/confirm/', confirm, name="appointment_confirm"),
    path('<int:id>/cancel/', cancel, name="appointment_cancel"),
]
