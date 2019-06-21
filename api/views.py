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

# Create your views here.

class Payment(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def get(self, request):
        # TODO надо реализовать добавление записи и поиск записей в бд
        api_access_token = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImY3M3htZy0wMCIsInVzZXJfaWQiOiI3OTMxOTc5MjIzOCIsInNlY3JldCI6ImE5NjY4OWE4OTJhZjczYzE2MTdiODdhZGE5MzM3MGE4NTVkYzYyYzJlZjc4ZjU5MzY0Nzg5ZjY4N2JkZTIxYjkifX0='
        buffer = request.data
        s = requests.Session()
        s.headers['authorization'] = 'Bearer ' + api_access_token
        timestamp = int(time.time())
        bill_id = str(timestamp * 1000) + str(random.randint(1000, 9999)) # + ID_user
        #print(ProjectTelNumberSerializer(Project.objects.get(name__exact=buffer['id_project'])).data['telNumber'])
        #print(UserEmailSerializer(User.objects.get(id__exact=buffer['id_user'])).data['email'])
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
                "phone": ProjectTelNumberSerializer(Project.objects.get(id__exact=buffer['id_project'])).data['telNumber'],
                "email": UserEmailSerializer(User.objects.get(id__exact=buffer['id_user'])).data['email'],
            },
            "customFields": {}
        }
        h1 = s.put('https://api.qiwi.com/partner/bill/v1/bills/' + bill_id, json=app_json_props)
        # Добавление транзакции в таблицу
        k = json.loads(h1.text)
        t = Transaction(id_user=User.objects.get(id__exact=buffer['id_user']), id_projects = Project.objects.get(id__exact=buffer['id_project']), payment = val, status = k['status']['value'], siteId = k['siteId'], billId= 'bill_id' , expirationTime=buffer['expirationTime'])
        t.save()

        return Response(h1, status=status.HTTP_200_OK)

# TODO требуется указать адрес сервера
class CheckPayment(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request):
        # TODO получить сигнатуру из запроса обновить статус транзакции в бд и currentAmount у проекта
        s = requests.Session()
        signature = ""
        buffer = request.data
        invoice_parameters = buffer['amount']['currency']+"|"+buffer['amount']['value']+"|"+buffer['billId']+"|"+buffer['siteId']+"|"+buffer['status']['value']
        api_access_token = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImY3M3htZy0wMCIsInVzZXJfaWQiOiI3OTMxOTc5MjIzOCIsInNlY3JldCI6ImE5NjY4OWE4OTJhZjczYzE2MTdiODdhZGE5MzM3MGE4NTVkYzYyYzJlZjc4ZjU5MzY0Nzg5ZjY4N2JkZTIxYjkifX0='
        dig = hmac.new(api_access_token, msg=invoice_parameters, digestmod=hashlib.sha256).digest()
        hash_var = base64.b64encode(dig).decode
        if hash_var == signature:
            h3 = s.get('https://api.qiwi.com/partner/bill/v1/bills/' + buffer['billId'])
            json.loads(h3.text)
            # TODO ответ - результат проверки 0
        else:
            a=1
            # TODO ответ - результат проверки не 0


class Registration (generics.CreateAPIView):
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
    serializer_class = UserSerializer
    Response(status=status.HTTP_201_CREATED)


class CreateProject (generics.CreateAPIView):
    serializer_class = ProjectSerializer
    Response(status=status.HTTP_201_CREATED)





