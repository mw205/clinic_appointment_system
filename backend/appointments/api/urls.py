from django.urls import path
from .views import confirm
from .views import cancel


urlpatterns = [
    path('<int:id>/confirm/', confirm, name="appointment_confirm"),
    path('<int:id>/cancel', cancel, name="appointment_cancel")
]