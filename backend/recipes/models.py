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


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name="Тэг")
    color = models.CharField(max_length=7, verbose_name="Цвет", blank=True, null=True)
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="URL_tag"
    )

    class Meta:
        verbose_name_plural = "Тэги"
        verbose_name = "Тэг"

    def __str__(self):
        return self.name
