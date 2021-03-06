from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
import time

# Create your models here.

# TODO эта модель не является дефолтной (создается отдельная таблица), подумать, как можно сделать юзеров в одной дефолтной модели
class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=30)
    name = models.CharField(max_length=30, unique=True)


class Project(models.Model):
    name = models.CharField(max_length=100)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User')
    targetAmount = models.FloatField()
    currentAmount = models.FloatField(default=0)
    description = models.TextField()
    isActive = models.BooleanField(default=True)
    TOPIC_TYPES = (
        (1, 'Science'),
        (2, 'IT'),
        (3, 'Entertainment'),
        (4, 'Other'),
    )
    topic = models.IntegerField(choices=TOPIC_TYPES)
    # TODO Для тегов надо подумать, как хранить их в базе
    '''
    
    '''
    # tags =
    date = models.DateTimeField(default=make_aware(datetime.fromtimestamp(time.time())).isoformat())
    # Дальше идут реквизиты
    telNumber = models.CharField(max_length=12, unique=False)


# Транзакции для QIWI, Yandex, RFI
class Transaction(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_projects = models.ForeignKey(Project, on_delete=models.CASCADE)
    payment = models.FloatField()
    STATUS_TYPES = (
        (1, 'WAITING'),  # выставлен ожидает оплаты
        (2, 'PAID'),  # оплачен
        (3, 'REJECTED'),  # отклонен
        (4, 'EXPIRED'),  # время жизни истекло, счёт не оплачен
    )

    PAYMENT_TYPE = (
        (1, 'QIWI'),
        (2, 'YANDEX'),
        (3, 'RFI')
    )

    status = models.IntegerField(choices=STATUS_TYPES)
    payment_type = models.IntegerField(choices=PAYMENT_TYPE)
    expirationTime = models.DateTimeField()
    siteId = models.TextField()
    billId = models.TextField()


class Authorization(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=150)



# TODO можно добавить комментарии, в модели ключ будет сслытаься на ключи внутри себя для реализации вложенности комментариев

