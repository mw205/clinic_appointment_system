from rest_framework.routers import DefaultRouter

from appointments.api.views import AppointmentViewSet

router = DefaultRouter()
router.register("", AppointmentViewSet)