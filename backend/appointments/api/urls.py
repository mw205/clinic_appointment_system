from django.urls import path

from .router import router
from .views import AppointmentBookingCreateAPIView


urlpatterns = [
    path("", AppointmentBookingCreateAPIView.as_view(), name="appointment_book"),
] + router.urls


# waleed change
# urlpatterns = [
#     path("book/", AppointmentBookingCreateAPIView.as_view(),
#          name="appointment_book"),
#     path('doctor/queue/', doctor_queue, name="doctor_queue"),
#     path('<int:id>/confirm/', confirm, name="appointment_confirm"),
#     path('<int:id>/cancel/', cancel, name="appointment_cancel"),
#     path('<int:id>/check-in/', check_in, name="appointment_detail"),
# ]
