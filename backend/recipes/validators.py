import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if not re.fullmatch('^\w+$', value):
        raise ValidationError("Неправильные символы в имени")
    if value == "me":
        raise ValidationError("Использование 'me' в качестве имени запрещено")


def validate_color_tag(value):
    if not re.fullmatch('#[A-Fa-f0-9]{2,6}', value):
        raise ValidationError("Цвет должен быть указан в HEX-формате")


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError("Приготовление не может быть меньше 1 мин.")


def validate_above_zero(value):
    if value < 1:
        raise ValidationError("Количество не может быть меньше единицы")
