from django.urls import path, include

urlpatterns = [
    path("", include("consultations.api.urls"))
]