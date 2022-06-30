# Generated by Django 4.0.5 on 2022-06-30 06:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_subscribe_subscribe_unique_user_following'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscribe',
            options={'ordering': ['user'], 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddField(
            model_name='user',
            name='subscription',
            field=models.ManyToManyField(through='recipes.Subscribe', to=settings.AUTH_USER_MODEL),
        ),
    ]