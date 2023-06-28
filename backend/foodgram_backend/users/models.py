from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Модель пользователя."""
    username = models.CharField("Логин", max_length=255, unique=True)
    email = models.EmailField("E-Mail", max_length=255, unique=True)
    first_name = models.CharField("Имя", max_length=255)
    last_name = models.CharField("Фамилия", max_length=255)
