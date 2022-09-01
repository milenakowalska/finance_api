from django.contrib.auth import login, logout
from rest_framework import permissions
from rest_framework import views
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
import coreapi
import coreschema
from rest_framework.schemas import ManualSchema

from . import serializers

class LoginView(views.APIView):
    """
    User login endpoint.
    POST body requires username and password.
    """

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
    ---
    post:
        parameters:
            - name: username
              type: string
    """

    schema = ManualSchema(
        fields=[
            coreapi.Field(
                'id',
                required=True,
                location='path',
                description='A unique integer value identifying specific your-model-name.',
                schema=coreschema.Integer(),
                ),
        ]
    )

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
