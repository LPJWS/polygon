from datetime import datetime, timedelta
import random
from typing import List
from django.db.models import deletion
from django.db.models.deletion import CASCADE
import django.db.models.deletion
import jwt as jwt
from django.contrib.auth.models import AbstractUser
from django.db import models
from configs import settings


class Group(models.Model):
    """
    [Group]
    Модель группы
    """

    title = models.CharField(max_length=50, null=True, blank=True, verbose_name="Название")

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Attachment(models.Model):
    """
    [Attachment]
    Модель прикрепляемого материала
    """
    title = models.CharField(max_length=50, default="Без названия", verbose_name="Название")
    file = models.FileField(upload_to='attaches', blank=False, verbose_name="Файл")

    def __str__(self) -> str:
        return str(self.title)

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


class User(AbstractUser):
    """
    [User]
    Переопределенный класс пользователя. Использует кастомный менеджер.
    """

    name = models.CharField(max_length=30, blank=True, null=True, verbose_name="ФИ пользователя")
    username = models.CharField(max_length=50, unique=True, verbose_name='email')
    photo = models.ImageField(upload_to='user_images', blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=deletion.SET_NULL, blank=True, null=True, verbose_name="Группа")

    USERNAME_FIELD = 'username'

    def __str__(self) -> str:
        return f"{self.name}"

    @property
    def token(self) -> str:
        return self._generate_jwt_token()

    def _generate_jwt_token(self) -> str:
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 30 дней от создания
        """
        dt = datetime.now() + timedelta(days=30)

        token = jwt.encode({
            'id': self.pk,
            'expire': str(dt)
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Task(models.Model):
    """
    [Task]
    Модель таска
    """

    title = models.CharField(max_length=50, null=True, blank=True, verbose_name="Название")
    desc = models.TextField(null=True, blank=True, verbose_name="Описание для студентов")
    flag = models.CharField(max_length=100, null=True, blank=True, verbose_name="Флаг (ответ)")
    order = models.IntegerField(default=0, verbose_name="Номер по порядку")
    is_manual = models.BooleanField(default=False, verbose_name="Таск оценивается вручную?")
    material = models.ManyToManyField(Attachment, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        verbose_name = 'Таск'
        verbose_name_plural = 'Таски'


class TaskSolve(models.Model):
    """
    [TaskSolve]
    Модель решенных тасков
    """

    task = models.ForeignKey(Task, on_delete=CASCADE, verbose_name="Таск")
    student = models.ForeignKey(User, on_delete=CASCADE, verbose_name="Студент")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время решения")
    date_accepted = models.DateTimeField(blank=True, null=True, verbose_name="Дата принятия отчета")

    def __str__(self) -> str:
        return f"{self.task.title} ({self.student.name} {self.student.group})"

    class Meta:
        verbose_name = 'Решенный таск'
        verbose_name_plural = 'Решенные таски'
