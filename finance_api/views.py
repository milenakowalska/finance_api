from django.contrib.auth import login, logout
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework import views
from rest_framework import status
from rest_framework import generics
from rest_framework import metadata
from rest_framework.response import Response

from . import serializers

class MinimalMetadata(metadata.BaseMetadata):
    """
    Return the name, description and body template.
    """
    def determine_metadata(self, request, view):
        return {
            'name': view.get_view_name(),
            'description': view.get_view_description(),
            'body template': view.get_body_template()
        }

class InfoView(views.APIView): 
    # available also for not logged in users
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response({"endpoints": ""}, status=status.HTTP_202_ACCEPTED)

class LoginView(views.APIView):
    """
    User login endpoint.
    POST body requires username and password.
    """
    metadata_class = MinimalMetadata

    # available also for not logged in users
    permission_classes = (permissions.AllowAny,)

    def get_body_template(self):
        return {"username": "required", "password": "required"}

    def post(self, request):
        serializer = serializers.LoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)

class RegisterView(views.APIView):
    """
    User register endpoint.
    POST body requires username, password and confirm_password fields.
    """
    metadata_class = MinimalMetadata

    # available also for not logged in users
    permission_classes = (permissions.AllowAny,)

    def get_body_template(self):
        return {
            "username": "required",
            "password": "required",
            "confirm_password": "required",
            "email": "optional",
            "first_name": "optional",
            "last_name": "optional"
            }

    def post(self, request):
        serializer = serializers.RegisterSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)

class ProfileView(generics.RetrieveAPIView):
    """
    Shows user data of the logged in user.
    """
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

class LogoutView(views.APIView):
    """
    User logout endpoint.
    """
    def post(self, request):
        logout(request)
        return Response(None, status=status.HTTP_202_ACCEPTED)
