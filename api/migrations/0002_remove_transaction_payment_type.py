# Generated by Django 2.2.2 on 2019-06-25 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='payment_type',
        ),
    ]
