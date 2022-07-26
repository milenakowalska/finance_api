from django.contrib.auth import login, logout
from rest_framework import permissions
from rest_framework import views
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
import coreapi
import coreschema
from rest_framework.schemas import ManualSchema
from .models import Contract, Saving, RecurringSaving
from . import serializers
from datetime import date


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
    serializer_class = serializers.RegisterSerializer

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

class ContractsList(views.APIView):
    """
    Manage contracts
    """
    serializer_class = serializers.ContractSerializer

    def get(self, request):
        all_contracts = Contract.objects.all().filter(user=self.request.user)
        serializer = self.serializer_class(all_contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        new_contract = {
            'name': self.request.data['name'],
            'user': self.request.user,
            'description': self.request.data['description'],
            'amount': self.request.data['amount'],
            'first_billing_day': self.request.data['first_billing_day'],
            'end_date': None if self.request.data['end_date'] == "" else self.request.data['end_date'],
            'billing_frequency': self.request.data['billing_frequency'],
        }

        serializer = self.serializer_class(data=new_contract)
        if serializer.is_valid(raise_exception=True):
            Contract.objects.create(**new_contract)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class SingleContract(views.APIView):
    """
    Manage single contract
    """
    serializer_class = serializers.ContractSerializer

    def get_object(self, pk):
        return Contract.objects.get(pk = pk)

    def get(self, request, pk):
        try:
            contract = self.get_object(pk)
            serializer = self.serializer_class(contract)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message":"not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        updated_contract = {
            'name': self.request.data['name'],
            'user': self.request.user,
            'description': self.request.data['description'],
            'amount': self.request.data['amount'],
            'first_billing_day': self.request.data['first_billing_day'],
            'end_date': None if self.request.data['end_date'] == "" else self.request.data['end_date'],
            'billing_frequency': self.request.data['billing_frequency'],
        }

        contract = self.get_object(pk)
        serializer = self.serializer_class(contract, data=updated_contract)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        try:
            contract = self.get_object(pk)
            contract.delete()
            return Response({"message":"contract deleted"}, status=status.HTTP_200_OK)
        except:
            return Response({"message":"error"}, status=status.HTTP_404_NOT_FOUND)


class RecurringSavingsList(views.APIView):
    """
    Manage recurring savings
    """
    serializer_class = serializers.RecurringSavingSerializer

    def get(self, request):
        all_recurring_savings = RecurringSaving.objects.all().filter(user=self.request.user)
        recurring_savings_serializer = self.serializer_class(all_recurring_savings, many=True)

        return Response(recurring_savings_serializer.data, status=status.HTTP_200_OK
        )
    
    def post(self, request):
        new_saving = {
            'name': self.request.data['name'],
            'user': self.request.user,
            'description': self.request.data['description'],
            'amount': self.request.data['amount'],
            'start_date': self.request.data['start_date'],
            'end_date': None if self.request.data['end_date'] == "" else self.request.data['end_date'],
            'pay_out_day': None if self.request.data['pay_out_day'] == "" else self.request.data['pay_out_day'],
            'frequency': self.request.data['frequency']
        }

        serializer = self.serializer_class(data=new_saving)
        if serializer.is_valid(raise_exception=True):
            RecurringSaving.objects.create(**new_saving)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleRecurringSaving(views.APIView):
    """
    Manage single recurring saving
    """
    serializer_class = serializers.RecurringSavingSerializer

    def get_object(self, pk):
        return RecurringSaving.objects.get(pk = pk)

    def get(self, request, pk):
        try:
            saving = self.get_object(pk)
            serializer = self.serializer_class(saving)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message":"not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        updated_saving = {
            'name': self.request.data['name'],
            'user': self.request.user,
            'description': self.request.data['description'],
            'amount': self.request.data['amount'],
            'start_date': self.request.data['start_date'],
            'end_date': None if self.request.data['end_date'] == "" else self.request.data['end_date'],
            'pay_out_day': None if self.request.data['pay_out_day'] == "" else self.request.data['pay_out_day'],
            'frequency': self.request.data['frequency']
        }

        saving = self.get_object(pk)
        serializer = self.serializer_class(saving, data=updated_saving)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        try:
            saving = self.get_object(pk)
            saving.delete()
            return Response({"message":"saving deleted"}, status=status.HTTP_200_OK)
        except:
            return Response({"message":"error"}, status=status.HTTP_404_NOT_FOUND)


class SavingsList(views.APIView):
    """
    Manage savings
    """
    serializer_class = serializers.SavingSerializer

    def get(self, request):
        all_savings = Saving.objects.all().filter(user=self.request.user)
        savings_serializer = self.serializer_class(all_savings, many=True)

        return Response(savings_serializer.data, status=status.HTTP_200_OK
        )
    
    def post(self, request):
        new_saving = {
            'name': self.request.data['name'],
            'user': self.request.user,
            'description': self.request.data['description'],
            'amount': self.request.data['amount'],
            'pay_out_day': None if self.request.data['pay_out_day'] == "" else self.request.data['pay_out_day']
        }

        serializer = self.serializer_class(data=new_saving)
        if serializer.is_valid(raise_exception=True):
            Saving.objects.create(**new_saving)

        return Response(serializer.data, status=status.HTTP_200_OK)



class SingleSaving(views.APIView):
    """
    Manage single saving
    """
    serializer_class = serializers.SavingSerializer

    def get_object(self, pk):
        return Saving.objects.get(pk = pk)

    def get(self, request, pk):
        try:
            saving = self.get_object(pk)
            serializer = self.serializer_class(saving)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message":"not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        updated_saving = {
            'name': self.request.data['name'],
            'user': self.request.user,
            'description': self.request.data['description'],
            'amount': self.request.data['amount'],
            'pay_out_day': None if self.request.data['pay_out_day'] == "" else self.request.data['pay_out_day']
        }

        saving = self.get_object(pk)
        serializer = self.serializer_class(saving, data=updated_saving)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        try:
            saving = self.get_object(pk)
            saving.delete()
            return Response({"message":"saving deleted"}, status=status.HTTP_200_OK)
        except:
            return Response({"message":"error"}, status=status.HTTP_404_NOT_FOUND)

    
class StatisticsView(views.APIView):
    """
    See statistics based on the current account balance
    """
    def get(self, request):
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = serializers.BalanceSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        total_account_balance = serializer.data['balance']
        user = self.request.user
        statistics = user.create_statistics(total_account_balance, date.today())
        return Response(statistics.show(), status=status.HTTP_202_ACCEPTED)


#TODO: Needs to be implemented
# class PrognoseView(views.APIView):
#     """
#     See prognose.
#     """
#     def get(self, request):
#         return Response(None, status=status.HTTP_200_OK)