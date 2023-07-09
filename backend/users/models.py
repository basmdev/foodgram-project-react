from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        "first_name",
        "last_name",
    )
    username = models.CharField(
        max_length=150, unique=True, verbose_name="username"
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name="Почта"
    )

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username[:35]


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Автор",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписчик",
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=("user", "author"), name="uq_follow")
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} подписан на {self.author}"[:35]
