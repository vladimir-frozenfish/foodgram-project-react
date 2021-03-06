# Generated by Django 4.0.5 on 2022-07-10 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0025_alter_recipe_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='shopping_cart_recipe',
            field=models.ManyToManyField(related_name='shopping_cart_recipe', through='recipes.ShoppingCartRecipe', to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='user',
            name='favorite_recipe',
            field=models.ManyToManyField(related_name='favorite_recipe', through='recipes.FavoriteRecipe', to='recipes.recipe'),
        ),
    ]
