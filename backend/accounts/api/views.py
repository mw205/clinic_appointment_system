from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied, NotFound

from accounts.api.serializers import LoginSerializer, UserSummarySerializer, CurrentUserSerializer, LogoutSerializer, PatientRegistrationSerializer, CurrentUserUpdateSerializer, CurrentPatientProfileSerializer, CurrentPatientProfileUpdateSerializer
from accounts.rbac import is_patient
from accounts.models import PatientProfile


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

        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': user_data
        },
        status=status.HTTP_200_OK
        )


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
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "detail": "Successfully logged out."
        },
        status=status.HTTP_200_OK
        )
       

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

        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': user_data
        },
        status=status.HTTP_201_CREATED
        )
    

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