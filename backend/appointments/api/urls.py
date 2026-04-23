from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentViewSet,
    cancel,
    check_in,
    confirm,
    doctor_queue,
)

router = DefaultRouter()
router.register("", AppointmentViewSet, basename="appointment")


urlpatterns = router.urls + [
    path("doctor/queue/", doctor_queue, name="doctor_queue"),
    path("<int:id>/confirm/", confirm, name="appointment_confirm"),
    path("<int:id>/cancel/", cancel, name="appointment_cancel"),
    path("<int:id>/check-in/", check_in, name="appointment_check_in"),
]
