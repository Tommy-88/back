# Generated by Django 2.2.2 on 2019-06-21 19:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190621_1810'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='tags',
        ),
        migrations.AlterField(
            model_name='project',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='project',
            name='id_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='User', to='api.User'),
        ),
    ]
