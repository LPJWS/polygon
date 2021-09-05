# Generated by Django 3.2.6 on 2021-09-05 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polygon', '0013_user_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Без названия', max_length=50, verbose_name='Название')),
                ('file', models.FileField(upload_to='attaches', verbose_name='Файл')),
            ],
            options={
                'verbose_name': 'Материал',
                'verbose_name_plural': 'Материалы',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='material',
            field=models.ManyToManyField(blank=True, null=True, to='polygon.Attachment'),
        ),
    ]
