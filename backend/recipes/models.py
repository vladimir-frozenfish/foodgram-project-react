from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=150,
                                unique=True)
    first_name = models.CharField(max_length=150,
                                  blank=True, null=True)
    last_name = models.CharField(max_length=150,
                                 blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)

    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"
        ordering = ["id"]

    def __str__(self):
        return self.username
