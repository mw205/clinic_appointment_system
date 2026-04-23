from rest_framework.routers import DefaultRouter

from scheduling.api.views import DoctorScheduleViewSet, ScheduleExceptionViewSet

router = DefaultRouter()
router.register("schedules", DoctorScheduleViewSet, basename="doctor_schedules")
router.register("exceptions", ScheduleExceptionViewSet, basename="schedule_exceptions")
