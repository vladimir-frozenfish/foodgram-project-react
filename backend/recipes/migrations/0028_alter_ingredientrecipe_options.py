# Generated by Django 4.0.5 on 2022-07-12 07:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0027_alter_subscribe_following'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'ordering': ['recipe'], 'verbose_name': 'Ингредиент в рецепте', 'verbose_name_plural': 'Ингредиенты в рецептах'},
        ),
    ]
