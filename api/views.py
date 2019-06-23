import binascii

from django.shortcuts import render
from django.views.generic import View
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from .serializers import *
import requests
import time
import json
import random
import hmac
import hashlib
import base64
from .models import *

# TODO сделать нормальные url; там, где нужно, реализовать получение данных с помощью GET параметров
# ДЛЯ ФРОНТА: посмотрите доки от Миши


# Обработчик для "Перечислить сумму на QIWI кошелек", отправляется json c параметрами, адрес http://localhost/api/v1/hello, запрос GET
"""
Пример json для запроса к API
    {
        "payment" : 100,
        "expirationTime" : "2018-04-15T14:30:00+03:00",
        "id_project" : 2,
        "id_user" : 5
    }
"""


class Payment(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def get(self, request):
        api_access_token = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImY3M3htZy0wMCIsInVzZXJfaWQiOiI3OTMxOTc5MjIzOCIsInNlY3JldCI6ImE5NjY4OWE4OTJhZjczYzE2MTdiODdhZGE5MzM3MGE4NTVkYzYyYzJlZjc4ZjU5MzY0Nzg5ZjY4N2JkZTIxYjkifX0='
        buffer = request.data
        s = requests.Session()
        s.headers['authorization'] = 'Bearer ' + api_access_token
        timestamp = int(time.time())
        bill_id = str(timestamp * 1000) + str(random.randint(1000, 9999))  # + ID_user
        # print(ProjectTelNumberSerializer(Project.objects.get(name__exact=buffer['id_project'])).data['telNumber'])
        # print(UserEmailSerializer(User.objects.get(id__exact=buffer['id_user'])).data['email'])
        val = format(float(buffer['payment']), '.2f')
        # Создание json для qiwi-запроса
        app_json_props = {
            "amount": {
                "currency": "RUB",
                "value": val,
            },
            "comment": "Test",
            "expirationDateTime": buffer['expirationTime'],
            "customer": {
                "phone": ProjectTelNumberSerializer(Project.objects.get(id__exact=buffer['id_project'])).data[
                    'telNumber'],
                "email": UserEmailSerializer(User.objects.get(id__exact=buffer['id_user'])).data['email'],
            },
            "customFields": {}
        }
        h1 = s.put('https://api.qiwi.com/partner/bill/v1/bills/' + bill_id, json=app_json_props)
        # Добавление транзакции в таблицу
        k = json.loads(h1.text)
        t = Transaction(id_user=User.objects.get(id__exact=buffer['id_user']),
                        id_projects=Project.objects.get(id__exact=buffer['id_project']), payment=val,
                        status=k['status']['value'], siteId=k['siteId'], billId='bill_id',
                        expirationTime=buffer['expirationTime'])
        t.save()
        """
            Формат ответа в доках "Перечислить сумму"
        """
        return Response(h1, status=status.HTTP_200_OK)


# Обработчик для получения уведомлений об оплате
# TODO требуется указать адрес сервера, пока не работает
class CheckPayment(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request):
        # TODO получить сигнатуру из запроса обновить статус транзакции в бд и currentAmount у проекта
        s = requests.Session()
        signature = ""
        buffer = request.data
        invoice_parameters = buffer['amount']['currency'] + "|" + buffer['amount']['value'] + "|" + buffer[
            'billId'] + "|" + buffer['siteId'] + "|" + buffer['status']['value']
        api_access_token = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImY3M3htZy0wMCIsInVzZXJfaWQiOiI3OTMxOTc5MjIzOCIsInNlY3JldCI6ImE5NjY4OWE4OTJhZjczYzE2MTdiODdhZGE5MzM3MGE4NTVkYzYyYzJlZjc4ZjU5MzY0Nzg5ZjY4N2JkZTIxYjkifX0='
        dig = hmac.new(api_access_token, msg=invoice_parameters, digestmod=hashlib.sha256).digest()
        hash_var = base64.b64encode(dig).decode
        if hash_var == signature:
            h3 = s.get('https://api.qiwi.com/partner/bill/v1/bills/' + buffer['billId'])
            json.loads(h3.text)
        else:
            a = 1


# Обработчик "Регистрация", отправляется json с параметрами, адрес http://localhost/api/v1/user/create, запрос POST
# TODO Можно сделать отправку уведомления на почту, по идее это делается не особо сложно
"""
    Пример json 
    {
        "email" : "example@ex.ex",
        "password" : "1234",
        "name" : "example"
    }
"""


class Registration(generics.CreateAPIView):
    # TODO Можно сделать отправку уведомления на почту, по идее это делается не особо сложно
    '''
        В settings.py прописать:
        EMAIL_HOST = 'smtp.gmail.com'
        EMAIL_HOST_USER = 'почта'
        EMAIL_HOST_PASSWORD = 'пароль от почты'
        EMAIL_PORT = 'по умолчанию 25'
        EMAIL_USE_TLS/SSL = True/False
        для гугла надо разрешить доступ
        https://myaccount.google.com/lesssecureapps
        во views.py импортировать
        from django.core.mail import send_mail
        Наверное стоит сделать какую-нибудь переменную типа sent=False/True
        subject = 'тема сообщения'
        message = 'содержание'
        send_mail(subject, message, 'ящик, из которого отсылается сообщение', ['куда отсылать'])
    '''
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)
    serializer_class = UserSerializer
    """
        ответ - статус 201
    """
    Response(status=status.HTTP_201_CREATED)


# Обработчик "Создание проекта пользователем", отправляется json с параметрами, адрес http://localhost/api/v1/project/create, запрос POST
"""
    Пример json
    {
        "name" : "example",
        "id_user" : 2,
        "targetAmount" : 100.0,
        "currentAmount" : 10.0,
        "description" : "example example",
        "topic" : 2,
        "telNumber" "+78005553535"
    }
"""


class CreateProject(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    """
        ответ - статус 201
    """
    Response(status=status.HTTP_201_CREATED)


# Обработчик "Вывести 20 проектов", сортировка по дате, адрес http://localhost/api/v1/show/projects, запрос GET
class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    queryset = Project.objects.all().order_by('date')[:20]
    """
        ответ - json файл с списком проектов
        Пример 
[
    {
        "id": 1,
        "name": "Example1",
        "targetAmount": 1000,
        "currentAmount": 100,
        "date": "2019-06-21T19:28:27Z"
    },
    {
        "id": 2,
        "name": "Example2",
        "targetAmount": 99,
        "currentAmount": 10,
        "date": "2019-06-22T12:33:00Z"
    },
    {
        "id": 3,
        "name": "Example 3 ",
        "targetAmount": 100,
        "currentAmount": 10,
        "date": "2019-06-22T12:33:57Z"
    }
]
    """


# Обработчик "Показать все проекты пользователя", отправляется json с параметрами, адрес http://localhost/api/v1/user/project, запрос GET
"""
Пример json
{
    "id" : 1
}
"""


class ShowUserProjectsView(APIView):

    def get(self, request):
        buffer = ProjectSerializerUser(Project.objects.filter(id_user=request.data['id']), many=True)
        return Response(buffer.data)


# Обработчик "Показать все проекты по выбранной теме", отправляется json с параметрами, адрес http://localhost/api/v1/project/topic, запрос GET
"""
Пример json
{
    "topic" : 2
}
"""


class ShowProjectsTopicView(APIView):
    def get(self, request):
        buffer = ProjectListSerializer(Project.objects.filter(topic=request.data['topic']), many=True)
        """
            Пример ответа
[
    {
        "id": 3,
        "name": "Example",
        "targetAmount": 100,
        "currentAmount": 10,
        "date": "2019-06-22T12:33:57Z"
    }
]
        """
        return Response(buffer.data)


# Обработчик "Сделать проект неактивным", отправляется json с параметрами, адрес http://localhost/api/v1/project/status, запрос PATCH
"""
Пример json
{
    "id": 2
}
"""


class ChangeProjectStatusView(APIView):
    def patch(self, request):
        buffer = Project.objects.get(id__exact=request.data['id'])
        buffer.isActive = False
        buffer.save()
        """
            ответ - статус 200
        """
        return Response(status=status.HTTP_200_OK)

    # request.data['id']


# Обработчик "Вывести информацию о проекте", отправляется json с параметрами, адрес http://localhost/api/v1/show/project, запрос GET
"""
{
    "id":2
}
"""


class ShowProjectView(APIView):

    def get(self, request):
        buffer = ProjectSerializer(Project.objects.get(id__exact=request.data['id']))
        """
            Пример ответа json
{
    "id": 2,
    "name": "jfsdflsjd",
    "targetAmount": 99,
    "currentAmount": 10,
    "description": "fdkjasifjlakjasdflksadjfskdlfjs",
    "isActive": false,
    "topic": 1,
    "date": "2019-06-22T12:33:00Z",
    "telNumber": "+79219791630",
    "id_user": 3
}
        """
        return Response(buffer.data)


