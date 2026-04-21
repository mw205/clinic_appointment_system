from django.urls import path, include

urlpatterns = [
    path('appointments/', include('appointments.api.urls'))
]