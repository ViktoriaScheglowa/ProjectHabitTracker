from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name='email',
        help_text='Введите Ваш email'
    )
    avatar = models.ImageField(
        upload_to='media/avatars',
        verbose_name='Аватар',
        help_text='Загрузите аватар',
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        max_length=35,
        verbose_name='Номер телефона',
        help_text='Введите номер телефона',
        null=True,
        blank=True
    )
    country = models.CharField(
        max_length=50,
        verbose_name='Страна',
        help_text='Введите страну проживания',
        null=True,
        blank=True
    )
    token = models.CharField(
        max_length=50,
        verbose_name='Токен',
        null=True,
        blank=True
    )
    chat_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Телеграм ID",
        help_text="Укажите Ваш ID telegram",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return 'media/default_avatar.png'
