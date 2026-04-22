from django.urls import path
from .views import AppointmentListCreateAPIView, AppointmentRetrieveAPIView, cancel, confirm


urlpatterns = [
    path("", AppointmentListCreateAPIView.as_view(), name="appointment_list_create"),
    path("<int:pk>/", AppointmentRetrieveAPIView.as_view(), name="appointment_detail"),
    path('<int:id>/confirm/', confirm, name="appointment_confirm"),
    path('<int:id>/cancel/', cancel, name="appointment_cancel"),
]
