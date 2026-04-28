from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend



from accounts.api.serializers import LoginSerializer, UserSummarySerializer, CurrentUserSerializer, LogoutSerializer, PatientRegistrationSerializer, CurrentUserUpdateSerializer, CurrentPatientProfileSerializer, CurrentPatientProfileUpdateSerializer, CurrentDoctorProfileSerializer,CurrentDoctorProfileUpdateSerializer, StaffUserSerializer, StaffUserUpdateSerializer, ChangePasswordSerializer
from accounts.rbac import is_patient, is_doctor, is_admin
from accounts.models import DoctorProfile, PatientProfile, User
from accounts.api.permissions import IsAdminOrReceptionist, IsAdminOnly


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=settings.AUTH_REFRESH_COOKIE_MAX_AGE,
        httponly=settings.AUTH_REFRESH_COOKIE_HTTP_ONLY,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )


def delete_refresh_cookie(response):
    response.delete_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
    )

class UserPagination(PageNumberPagination):
    page_size = 20

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)
        access_token = str(refresh.access_token)

        # serialize user
        user_data = UserSummarySerializer(user).data

        response = Response({
            'access': access_token,
            'user': user_data
        },
        status=status.HTTP_200_OK
        )
        set_refresh_cookie(response, refresh_token)
        return response


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        user = request.user
        serializer = CurrentUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        user = request.user
        serializer = CurrentUserUpdateSerializer(instance=user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(CurrentUserSerializer(user).data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            instance=request.user,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        refresh_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        response = Response(
            {"detail": "Password updated successfully. Please log in again."},
            status=status.HTTP_200_OK,
        )
        delete_refresh_cookie(response)
        return response
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = LogoutSerializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response({
            "detail": "Successfully logged out."
        },
        status=status.HTTP_200_OK
        )
        delete_refresh_cookie(response)
        return response
       

class PatientRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatientRegistrationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)
        access_token = str(refresh.access_token)

        user_data = UserSummarySerializer(user).data

        response = Response({
            'access': access_token,
            'user': user_data
        },
        status=status.HTTP_201_CREATED
        )
        set_refresh_cookie(response, refresh_token)
        return response


class RefreshTokenCookieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        response_data = {
            "access": serializer.validated_data["access"],
        }
        response = Response(response_data, status=status.HTTP_200_OK)

        rotated_refresh_token = serializer.validated_data.get("refresh")
        if rotated_refresh_token:
            set_refresh_cookie(response, rotated_refresh_token)

        return response
    

class CurrentPatientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request):
        user = request.user
        if not is_patient(user):
            raise PermissionDenied("Only patients can access this resource.")
        
        try:
            return user.patientprofile
        except PatientProfile.DoesNotExist:
            raise NotFound("Patient profile not found.")
        
    def get(self, request):
        profile = self.get_object(request)

        serializer = CurrentPatientProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def patch(self, request):
        profile = self.get_object(request)

        serializer = CurrentPatientProfileUpdateSerializer(instance=profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        return Response(CurrentPatientProfileSerializer(profile).data, status=status.HTTP_200_OK)

class CurrentDoctorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request):
        user = request.user
        if not is_doctor(user):
            raise PermissionDenied("Only doctors can access this resource.")
        
        try:
            return user.doctorprofile
        except DoctorProfile.DoesNotExist:
            raise NotFound("Doctor profile not found.")
        
    def get(self, request):
        profile = self.get_object(request)

        serializer = CurrentDoctorProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def patch(self, request):
        profile = self.get_object(request)

        serializer = CurrentDoctorProfileUpdateSerializer(instance=profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        return Response(CurrentDoctorProfileSerializer(profile).data, status=status.HTTP_200_OK)
    

class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsAdminOrReceptionist]
    queryset = (
        User.objects.prefetch_related("groups").all().order_by("id")
    )
    serializer_class = StaffUserSerializer
    pagination_class = UserPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    http_method_names = ["get", "patch", "head", "options"]

    def get_permissions(self):
        if self.action == "partial_update":
            return [IsAuthenticated(), IsAdminOnly()]
        return [IsAuthenticated(), IsAdminOrReceptionist()]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(groups__name=role)
        return queryset

    def partial_update(self, request, *args, **kwargs):
        user = request.user

        if not is_admin(user):
            raise PermissionDenied("Only admin users can update staff user details.")
        
        instance = self.get_object()
        serializer = StaffUserUpdateSerializer(instance=instance, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        output_serializer = StaffUserSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

