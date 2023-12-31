from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint


class User(AbstractUser):
    """Класс пользователей."""

    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True,
        db_index=True
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='фамилия'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='пароль'
    )
    is_admin = models.BooleanField(
        verbose_name='администратор',
        default=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Класс для подписки на авторов контента."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('id',)
        constraints = (
            UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_subscription'
            ),
        )

    def __str__(self):
        return f'{self.subscriber} подписан на: {self.author}'
