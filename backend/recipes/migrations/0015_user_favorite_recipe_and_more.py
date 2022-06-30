# Generated by Django 4.0.5 on 2022-06-30 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_favoriterecipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='favorite_recipe',
            field=models.ManyToManyField(through='recipes.FavoriteRecipe', to='recipes.recipe'),
        ),
        migrations.AddConstraint(
            model_name='favoriterecipe',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_user_favorite_recipe'),
        ),
    ]