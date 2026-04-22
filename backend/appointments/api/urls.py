from django.urls import path

from .router import router
from .views import AppointmentBookingCreateAPIView


urlpatterns = [
    path("", AppointmentBookingCreateAPIView.as_view(), name="appointment_book"),
]+ router.urls
