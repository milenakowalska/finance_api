from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Contract, Saving, RecurringSaving
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            'id',
            'name',
            'description',
            'amount',
            'first_billing_day',
            'end_date',
            'billing_frequency',
        ]

class SavingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saving
        fields = [
            'id',
            'name',
            'description',
            'amount',
            'pay_out_day'
        ]

class RecurringSavingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringSaving
        fields = [
            'id',
            'name',
            'description',
            'amount',
            'start_date',
            'end_date',
            'frequency',
        ]

class LoginSerializer(serializers.Serializer):
    """
    TODO: Add Docstring
    """
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                message = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(message, code='authorization')
        
        else:
            message = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(message, code='authorization')

        attrs['user'] = user
        return attrs

class RegisterSerializer(serializers.Serializer):
    """
    TODO: Add Docstring
    """
    username = serializers.CharField(label="Username")
    confirm_password = serializers.CharField(label="Confirm_password")
    password = serializers.CharField(label="Password", trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if not username or not password or not confirm_password:
            message = 'Registration failed: all fields are required.'
            raise serializers.ValidationError(message, code='authorization')
        
        elif password != confirm_password:
            message = 'Registration failed: Password must match'
            raise serializers.ValidationError(message, code='authorization')

        new_user = User.objects.create_user(username = username, password = password)
        new_user.save()

        attrs['user'] = new_user
        return attrs