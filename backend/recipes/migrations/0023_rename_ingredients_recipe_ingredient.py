# Generated by Django 4.0.5 on 2022-07-05 07:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0022_rename_tags_recipe_tag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='ingredients',
            new_name='ingredient',
        ),
    ]