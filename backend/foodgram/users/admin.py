from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс настройки раздела пользователей."""

    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'is_admin'
    )


@admin.register(Subscribe)
class SubscriptionAdmin(admin.ModelAdmin):
    """Класс настройки раздела подписок."""

    list_display = (
        'pk',
        'author',
        'subscriber',
    )

