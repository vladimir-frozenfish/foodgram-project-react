# Generated by Django 4.0.5 on 2022-07-11 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0026_user_shopping_cart_recipe_alter_user_favorite_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='following',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribe_user', to=settings.AUTH_USER_MODEL, verbose_name='Автор на которого подписывается'),
        ),
    ]
