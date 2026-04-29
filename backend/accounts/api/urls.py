from django.urls import path
from rest_framework.routers import DefaultRouter


from accounts.api.views import (
    ChangePasswordView,
    CurrentPatientProfileView,
    CurrentUserView,
    LoginView,
    LogoutView,
    PatientRegistrationView,
    RefreshTokenCookieView,
    CurrentDoctorProfileView,
    ResetPasswordView,
    UserViewSet,
    ForgotPasswordView
)
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('me/patient-profile/', CurrentPatientProfileView.as_view(), name='current-patient-profile'),
    path('me/doctor-profile/', CurrentDoctorProfileView.as_view(), name='current-doctor-profile'),
    path('refresh/', RefreshTokenCookieView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', PatientRegistrationView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]

urlpatterns += router.urls
