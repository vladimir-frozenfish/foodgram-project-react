# Generated by Django 4.0.5 on 2022-07-04 11:14

from django.db import migrations, models
import recipes.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0018_shoppingcartrecipe_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[recipes.validators.validate_username]),
        ),
    ]
