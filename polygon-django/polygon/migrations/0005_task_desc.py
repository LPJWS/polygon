# Generated by Django 3.2.6 on 2021-09-05 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polygon', '0004_auto_20210905_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='desc',
            field=models.TextField(blank=True, null=True, verbose_name='Описание для студентов'),
        ),
    ]
