from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import (
   RetrieveUpdateDestroyAPIView
)
from rest_framework.throttling import UserRateThrottle

from .permissions import IsOwner
from .serializers import UserRegisterAPIViewSerializer, ProfileAPIViewSerializer


class RegisterAPIView(CreateAPIView):
    serializer_class = UserRegisterAPIViewSerializer
    throttle_classes = [UserRateThrottle]

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ProfileAPIViewSerializer
    throttle_classes = [UserRateThrottle]

    def get_object(self):
        return self.request.user
