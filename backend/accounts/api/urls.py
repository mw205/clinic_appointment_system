from django.urls import path

from .views import (
    CurrentPatientProfileView,
    CurrentUserView,
    LoginView,
    LogoutView,
    PatientRegistrationView,
    RefreshTokenCookieView,
)



urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('me/patient-profile/', CurrentPatientProfileView.as_view(), name='current-patient-profile'),
    path('refresh/', RefreshTokenCookieView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', PatientRegistrationView.as_view(), name='register'),
]
