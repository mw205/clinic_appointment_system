from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny 

from rest_framework_simplejwt.tokens import RefreshToken

from accounts.api.serializers import LoginSerializer, UserSummarySerializer


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
