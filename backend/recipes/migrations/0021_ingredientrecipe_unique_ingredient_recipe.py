# Generated by Django 4.0.5 on 2022-07-05 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_rename_ingredient_recipe_ingredients_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_ingredient_recipe'),
        ),
    ]