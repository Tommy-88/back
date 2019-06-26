import binascii
from django.shortcuts import render
from django.views.generic import View
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework import generics
from .serializers import *
from datetime import datetime
import requests
import secrets
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


def create_transaction(amount, payment_type, id_user, id_projects, id_site=None):
    timestamp = int(time.time())
    bill_id = str(timestamp * 1000) + str(random.randint(1000, 9999))
    return Transaction(
        id_user=id_user,
        id_projects=id_projects,
        payment_type=payment_type,
        payment=amount,
        status=1,
        siteId=id_site,
        billId=bill_id,
        expirationTime=make_aware(datetime.fromtimestamp(time.time() + 7200))
    )


class Payment(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request):
        # Ссылка для успешной оплаты
        successURL = "http://success"

        stk = Authorization.objects.filter(token=request.META['HTTP_AUTHORIZATION']).count()
        if stk == 1:
            buffer = request.data
            payment_type = buffer['payment_type']

            transaction = create_transaction(
                amount=buffer['payment'],
                payment_type=payment_type,
                id_user=User.objects.get(id__exact=buffer['id_user']),
                id_projects=Project.objects.get(id__exact=buffer['id_project'])
            )

            if payment_type == "2":
                # Подтянуть с фронта при выборе яндекса "PC" - кошелек, "AC" - банковская карта
                yandex_payment_type = buffer['yandex_payment_type']

                url = "https://money.yandex.ru/quickpay/confirm.xml?receiver=410011023824487&label=" + \
                transaction.billId + "&quickpay-form=donate&targets=Crowdfunding&need-fio=false&need-email=false&" + \
                "need-phone=false&need-address=false&successURL=" + successURL + "&paymentType=" + \
                yandex_payment_type + "&sum=" + format(float(transaction.payment), '.2f')

                response = "{'payUrl':'" + url + "'}"

                return Response(response, status=status.HTTP_200_OK)
            elif payment_type == "3":
                url = "https://partner.rficb.ru/alba/input/?key=tAZ61uoeUQ2cobNpP1J4BEN9BPN29nz7p8r2n3Lg5VU=&" + \
                      "cost=" + format(float(transaction.payment), '.2f') + "&name=Crowdfunding&order_id=" + \
                      transaction.billId

                response = "{'payUrl':'" + url + "'}"

                return Response(response, status=status.HTTP_200_OK)
            else:
                api_access_token = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImY3M3htZy0wMCIsInVzZXJfaWQiOiI3OTMxOTc5MjIzOCIsInNlY3JldCI6ImE5NjY4OWE4OTJhZjczYzE2MTdiODdhZGE5MzM3MGE4NTVkYzYyYzJlZjc4ZjU5MzY0Nzg5ZjY4N2JkZTIxYjkifX0='
                s = requests.Session()
                s.headers['authorization'] = 'Bearer ' + api_access_token

                # timestamp = int(time.time())
                # bill_id = str(timestamp * 1000) + str(random.randint(1000, 9999))  # + ID_user





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
                    "expirationDateTime": transaction.expirationTime.isoformat(),
                    "customer": {
                        "phone": ProjectTelNumberSerializer(Project.objects.get(id__exact=buffer['id_project'])).data[
                            'telNumber'],
                        "email": UserEmailSerializer(User.objects.get(id__exact=buffer['id_user'])).data['email'],
                    },
                    "customFields": {}
                }

                h1 = s.put('https://api.qiwi.com/partner/bill/v1/bills/' + transaction.billId, json=app_json_props)
                # Добавление транзакции в таблицу
                k = json.loads(h1.text)

                transaction.siteId = k['siteId']
                transaction.save()

                """
                t = Transaction(id_user=User.objects.get(id__exact=buffer['id_user']),
                                id_projects=Project.objects.get(id__exact=buffer['id_project']), payment=val,
                                status=1, siteId=k['siteId'], billId='bill_id',
                                expirationTime=buffer['expirationTime'])
                t.save()
                """
                """
                    Формат ответа в доках "Перечислить сумму"
                """
                response = "{'payUrl':'" + k['payUrl'] + "'}"

                return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

# Обработчик для получения уведомлений об оплате
class CheckPayment(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request):
        s = requests.Session()
        signature = request.META['HTTP_X_API_SIGNATURE_SHA256']
        buffer = request.data
        invoice_parameters = buffer['amount']['currency'] + "|" + buffer['amount']['value'] + "|" + buffer[
            'billId'] + "|" + buffer['siteId'] + "|" + buffer['status']['value']
        api_access_token = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImY3M3htZy0wMCIsInVzZXJfaWQiOiI3OTMxOTc5MjIzOCIsInNlY3JldCI6ImE5NjY4OWE4OTJhZjczYzE2MTdiODdhZGE5MzM3MGE4NTVkYzYyYzJlZjc4ZjU5MzY0Nzg5ZjY4N2JkZTIxYjkifX0='

        dig = hmac.digest(api_access_token, msg=invoice_parameters, digest=hashlib.sha256)
        print(signature)
        print(dig)
        if dig == signature:
            h3 = s.get('https://api.qiwi.com/partner/bill/v1/bills/' + buffer['billId'])
            k=json.loads(h3.text)
            t = Transaction.objects.filter(billId=k['billId'])
            pr=Project.objects.filter(id__exact=t.id_user)
            pr.currentAmount+=float(k['value'])
            pr.save()
            t.status = 2
            t.save()
            return Response({"error" : "0"}, status=status.HTTP_200_OK)
        else:
            return Response({"error" : "1"})

# Обработчик "Регистрация", отправляется json с параметрами, адрес http://localhost/api/v1/user/create, запрос POST
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


class CreateProject(APIView):
    def post(self, request):
        stk = Authorization.objects.filter(token=request.META['HTTP_AUTHORIZATION']).count()
        buffer = request.data
        if stk == 1:
            k = Project()
            k.name = buffer['name']
            k.id_user = User.objects.get(id=buffer['id_user'])
            k.targetAmount = buffer['targetAmount']
            k.currentAmount = 0
            k.description = buffer['description']
            k.topic = buffer['topic']
            k.telNumber = buffer['telNumber']
            k.save()
            return Response(status=status.HTTP_201_CREATED)
            '''     
            ответ - статус 201
            '''
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


# Обработчик "Вывести 20 проектов", сортировка по дате, адрес http://localhost/api/v1/show/projects, запрос GET
class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    queryset = Project.objects.all().order_by('date').reverse()
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

    def post(self, request):
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
    def post(self, request):
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
        stk = Authorization.objects.filter(token=request.META['HTTP_AUTHORIZATION']).count()
        if stk == 1:
            buffer = Project.objects.get(id__exact=request.data['id'])
            buffer.isActive = False
            buffer.save()
            """
                ответ - статус 200
            """
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    # request.data['id']


# Обработчик "Вывести информацию о проекте", отправляется json с параметрами, адрес http://localhost/api/v1/show/project, запрос GET
"""
{
    "id":2
}
"""


class ShowProjectView(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request):
        buffer = Project.objects.get(id__exact=request.data['id'])
        s = ProjectShowSerializer(buffer)
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
        return Response(s.data)


class AuthorizationView(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request):
        buffer = request.data
        staff = User.objects.filter(email=buffer['email'], password=buffer['password']).count()
        if staff == 0:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            d = Authorization()
            d.id_user=User.objects.get(email=buffer['email'])
            d.token=secrets.token_hex(16)
            d.save()
            k = AuthorizationSerializer(Authorization.objects.filter(id_user=User.objects.get(email=buffer['email']).id),  many=True)
            return Response(k.data, status=status.HTTP_200_OK)


class GetPayment(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request):
        stk = Authorization.objects.filter(token=request.META['HTTP_AUTHORIZATION']).count()
        if stk == 1:
            buffer = Transaction.objects.get(billId=request.data['billId'])
            s = TransactionSerializer(buffer)
            return Response(s.data)



class DeAuthorizationView(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)
    def post(self, request):
        stk = Authorization.objects.filter(token=request.META['HTTP_AUTHORIZATION']).count()
        buffer = request.data
        if stk == 1:
            Authorization.objects.filter(token=request.META['HTTP_AUTHORIZATION']).delete()
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class ChangeDescriptionProjectView(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)
    def patch(self, request):
        stk = Authorization.objects.filter(token=request.META['HTTP_AUTHORIZATION']).count()
        if stk == 1:
            p = Project.objects.get(id_exact=request.data['id'])
            p.telNumber = request.data['telNumber']
            p.topic = request.data['topic']
            p.description = request.data['description']
            p.targetAmount = request.data['targetAmount']
            p.name = request.data['name']
            p.date = request.data['date']
            p.isActive = request.data['isActive']
            p.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

class YandexCallbackView(APIView):
    renderer_classes = (JSONRenderer,)

    def check_hash(self, **kwargs):
        prepared = \
            kwargs.get("notification_type", "") + "&" + \
            kwargs.get("operation_id", "") + "&" + \
            kwargs.get("amount", "") + "&" + \
            kwargs.get("currency", "") + "&" + \
            kwargs.get("datetime", "") + "&" + \
            kwargs.get("sender", "") + "&" + \
            kwargs.get("codepro", "") + "&" + \
            kwargs.get("notification_secret", "") + "&" + \
            kwargs.get("label", "")

        signature = hashlib.sha1(prepared.encode()).hexdigest()
        return signature == kwargs.get("sha1_hash")

    def post(self, request):
        yamoney_secret = 'gdsU+UQl3k/9bOziaeWWWGoV'

        validation_result = self.check_hash(
                notification_type=request.data['notification_type'],
                operation_id=request.data['operation_id'],
                amount=request.data['amount'],
                currency=request.data['currency'],
                datetime=request.data['datetime'],
                sender=request.data['sender'],
                codepro=request.data['codepro'],
                notification_secret=yamoney_secret,
                label=request.data['label'],
                sha1_hash=request.data['sha1_hash'])

        if not validation_result:
            print("Yandex.money notification data validation failed. Request:")
            print(request.data)
            return Response(status=status.HTTP_200_OK)

        # payment id stored in label field
        payment_id = request.data['label']

        try:
            transaction = Transaction.objects.get(billId=payment_id)
        except Transaction.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        if request.data['unaccepted'] == "true":
            print("Transaction unaccepted")
            return Response(status=status.HTTP_200_OK)

        transaction.status = 2
        transaction.save()

        return Response(status=status.HTTP_200_OK)


class RFIBankCallbackView(APIView):
    renderer_classes = (JSONRenderer,)

    def check_hash(self, **kwargs):
        prepared = \
            kwargs.get("tid", "") + \
            kwargs.get("name", "") + \
            kwargs.get("comment", "") + \
            kwargs.get("partner_id", "") + \
            kwargs.get("service_id", "") + \
            kwargs.get("order_id", "") + \
            kwargs.get("type", "") + \
            kwargs.get("partner_income", "") + \
            kwargs.get("system_income", "")

        prepared += kwargs.get("secret", "")
        print(prepared)
        signature = hashlib.md5(prepared.encode()).hexdigest()
        print(signature)
        return signature == kwargs.get("check")

    def post(self, request):
        rfibank_secret = 'ad64bdb6c1'

        validation_result = self.check_hash(
                tid=request.data['tid'],
                name=request.data['name'],
                comment=request.data['comment'],
                partner_id=request.data['partner_id'],
                service_id=request.data['service_id'],
                order_id=request.data['order_id'],
                type=request.data['type'],
                partner_income=request.data['partner_income'],
                system_income=request.data['system_income'],
                check=request.data['check'],
                secret=rfibank_secret,
                )

        if not validation_result:
            print("RFI Bank notification data validation failed. Request:")
            print(request.data)
            return Response(status=status.HTTP_200_OK)

        # payment id stored in label field
        payment_id = request.data['order_id']

        try:
            transaction = Transaction.objects.get(billId=payment_id)
        except Transaction.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        transaction.status = 2
        transaction.save()

        return Response(status=status.HTTP_200_OK)
