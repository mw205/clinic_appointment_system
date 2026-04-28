from rest_framework.routers import DefaultRouter
from consultations.api.views import (
    ConsultationRecordViewSet,
    PrescriptionItemViewSet,
    RequestedTestViewSet,
)

router = DefaultRouter()
router.register("consultations", ConsultationRecordViewSet, basename="consultations")
router.register("prescriptions", PrescriptionItemViewSet, basename="prescriptions")
router.register("tests", RequestedTestViewSet, basename="tests")