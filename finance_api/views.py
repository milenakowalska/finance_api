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
    schema = ManualSchema(
        description="User login endpoint.",
        fields=[
            coreapi.Field(
                'username',
                required=True,
                description='A unique username',
                location='path',
                schema=coreschema.String(),
                ),
            coreapi.Field(
                'password',
                required=True,
                description='Password',
                location='path',
                schema=coreschema.String(),
                ),
        ]
    )

    # available also for not logged in users
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.LoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)

class RegisterView(views.APIView):

    schema = ManualSchema(
        description="User register endpoint.",
        fields=[
            coreapi.Field(
                'username',
                required=True,
                description='A unique username',
                location='path',
                schema=coreschema.String(),
                ),
            coreapi.Field(
                'password',
                required=True,
                description='Password',
                location='path',
                schema=coreschema.String(),
                ),
            coreapi.Field(
                'confirm_password',
                required=True,
                description='Confirm password',
                location='path',
                schema=coreschema.String(),
                ),
            coreapi.Field(
                'first_name',
                required=False,
                description='First name - optional',
                location='path',
                schema=coreschema.String(),
                ),
        ]
    )

    # available also for not logged in users
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.RegisterSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)

class ProfileView(generics.RetrieveAPIView):
    """
    Shows user data of the logged in user.
    Accessible only for authorized users.
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

class ContractsView(views.APIView):
    """
    Manage contracts
    """
    def get_object(self, pk):
        return Response(None, status=status.HTTP_200_OK)

    def get(self, request):
        return Response(None, status=status.HTTP_200_OK)
    
    def post(self, request):
        return Response(None, status=status.HTTP_202_ACCEPTED)

    def put(self, request):
        return Response(None, status=status.HTTP_202_ACCEPTED)

    
class BalanceView(views.APIView):
    """
    See balance
    """
    def get(self, request):
        return Response(None, status=status.HTTP_200_OK)

class PrognoseView(views.APIView):
    """
    See prognose
    """
    def get(self, request):
        return Response(None, status=status.HTTP_200_OK)