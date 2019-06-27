from rest_framework import serializers
from .models import *


# Сериалайзеры со всеми полями для каждой модели

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


# Сериалайзеры для обработчиков с нужными полями

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


class ProjectSerializerUser(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        depth = 1


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        depth = 1


class ProjectShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        depth = 1


class UserAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']


class AuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authorization
        fields = '__all__'
        depth = 1


