# Generated by Django 3.2.6 on 2021-09-05 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polygon', '0008_auto_20210905_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_manual',
            field=models.BooleanField(default=False, verbose_name='Таск оценивается вручную?'),
        ),
    ]