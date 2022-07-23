from django.contrib.auth import login, logout
from rest_framework import permissions
from rest_framework import views
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response

from . import serializers

class LoginView(views.APIView):
    # Accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.LoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)

class RegisterView(views.APIView):
    # Accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.RegisterSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)

class ProfileView(generics.RetrieveAPIView):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

class LogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return Response(None, status=status.HTTP_202_ACCEPTED)
