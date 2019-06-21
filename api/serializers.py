from rest_framework import serializers
from .models import *


class ProjectSerializer(serializers.Serializer):
    class Meta:
        model = Project
        fields = '__all__'


class TransactionSerializer(serializers.Serializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email'
        ]


class ProjectTelNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'telNumber'
        ]
