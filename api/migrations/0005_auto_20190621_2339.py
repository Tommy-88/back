# Generated by Django 2.2.2 on 2019-06-21 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20190621_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='payment',
            field=models.FloatField(),
        ),
    ]
