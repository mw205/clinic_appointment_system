from rest_framework.routers import DefaultRouter
from analytics.api.views import AnalyticsSummaryViewSet

router = DefaultRouter()
router.register('', AnalyticsSummaryViewSet, basename='analytics')