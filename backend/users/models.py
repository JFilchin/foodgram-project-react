from api.validators import UsernameValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    '''Модель пользователя.'''
    username = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+\Z',
                           message='Допустимые символы: . + - '),
            UsernameValidator(),
        ],
        unique=True,
        blank=False,
        null=False,
        verbose_name='Пользователь'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Адрес электронной почты'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    '''Модель подписок для пользователя.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецепта'
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscription'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} {self.author}'
