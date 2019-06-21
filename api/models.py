from django.db import models
from django.utils import timezone

# Create your models here.

# TODO эта модель не является дефолтной (создается отдельная таблица), подумать, как можно сделать юзеров в одной дефолтной моедли
# TODO подумать, как сделать авторизацию
class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=30)
    name = models.CharField(max_length=30, unique=True)


class Project(models.Model):
    name = models.CharField(max_length=100)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User')
    targetAmount = models.FloatField()
    currentAmount = models.FloatField()
    description = models.TextField()
    isActive = models.BooleanField(default=True)
    # TODO обсудить, какие темы будут, добавить
    TOPIC_TYPES = (
        (1, 'Science'),
        (2, 'IT'),
        (3, 'Entertainment'),
        (4, 'Other'),
    )
    topic = models.IntegerField(choices=TOPIC_TYPES)
    # TODO Для тегов надо подумать, как хранить их в базе
    # tags =
    date = models.DateTimeField(default=timezone.now)
    # Дальше идут реквизиты
    telNumber = models.CharField(max_length=12, unique=True)


class Transaction(models.Model):
    # TODO Billid должен быть рандомное 6 значное число+unix - время в формате string; подумать, можно ли обойтись только им, как тогда его генерировать, если нет, то сдлеать id и BillId отдельно
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_projects = models.ForeignKey(Project, on_delete=models.CASCADE)
    payment = models.FloatField()
    status = models.TextField()
    expirationTime = models.CharField(max_length=120)
    siteId = models.TextField()
    billId = models.TextField()

# TODO обсудить добавление комментариев, продумать модель

