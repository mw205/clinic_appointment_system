from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, CurrentUserView, LogoutView



urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]