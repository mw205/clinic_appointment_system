from django.urls import path, include

urlpatterns = [
    path("", include("scheduling.api.urls"))
]
