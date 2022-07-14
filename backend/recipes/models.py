from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import (validate_above_zero,
                         validate_cooking_time,
                         validate_color_tag,
                         validate_username)


class User(AbstractUser):
    username = models.CharField(validators=[validate_username],
                                max_length=150,
                                unique=True)
    first_name = models.CharField(max_length=150,
                                  blank=True, null=True)
    last_name = models.CharField(max_length=150,
                                 blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    subscription = models.ManyToManyField("self", through="Subscribe")
    favorite_recipe = models.ManyToManyField(
        "Recipe",
        through="FavoriteRecipe",
        related_name="favorite_recipe"
    )
    shopping_cart_recipe = models.ManyToManyField(
        "Recipe",
        through="ShoppingCartRecipe",
        related_name="shopping_cart_recipe"
    )

    def get_subscription(self):
        return ", ".join(
            self.subscription.all().values_list('username', flat=True)
        )

    get_subscription.short_description = "Подписки на пользователей"

    def get_favorite_recipe(self):
        return ", ".join(
            self.favorite_recipe.all().values_list('name', flat=True)
        )

    get_favorite_recipe.short_description = "Избранные рецепты"

    def get_shopping_cart_recipe(self):
        return ", ".join(
            self.shopping_cart_recipe.all().values_list('name', flat=True)
        )

    get_shopping_cart_recipe.short_description = "Рецепты в корзине"

    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"
        ordering = ["id"]

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name="Тэг", unique=True)
    color = models.CharField(validators=[validate_color_tag],
                             max_length=7,
                             verbose_name="Цвет",
                             blank=True,
                             null=True)
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="URL_tag"
    )

    class Meta:
        verbose_name_plural = "Тэги"
        verbose_name = "Тэг"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name="Ингредиент")
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name_plural = "Ингредиенты"
        verbose_name = "Ингредиент"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name="Имя рецепта",
                            unique=True)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[validate_cooking_time],
        verbose_name="Время приготовления"
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    tag = models.ManyToManyField(Tag, through="TagRecipe")
    ingredient = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        blank=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта"
    )

    def get_tag(self):
        return ", ".join(self.tag.all().values_list("name", flat=True))

    get_tag.short_description = "Тэги рецепта"

    def get_ingredient(self):
        ingredients = IngredientRecipe.objects.filter(recipe=self.id)
        return ", ".join((map(str, ingredients)))

    get_ingredient.short_description = "Ингредиенты рецепта"

    class Meta:
        verbose_name_plural = "Рецепты"
        verbose_name = "Рецепт"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Тэги в рецепте"
        verbose_name = "Тэг в рецепте"
        ordering = ["recipe"]

        constraints = [
            models.UniqueConstraint(
                fields=["tag", "recipe"],
                name="unique_tag_recipe"
            )
        ]

    def __str__(self):
        return f"{self.tag} {self.recipe}"


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[validate_above_zero],
        verbose_name="Количество"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Ингредиенты в рецептах"
        verbose_name = "Ингредиент в рецепте"
        ordering = ["recipe"]

        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="unique_ingredient_recipe"
            )
        ]

    def __str__(self):
        return (f"{self.ingredient} "
                f"{self.amount} "
                f"{self.ingredient.measurement_unit}")


class Subscribe(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name="Подписчик")
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribe_user",
        verbose_name="Автор на которого подписывается"
    )

    class Meta:
        verbose_name_plural = "Подписки"
        verbose_name = "Подписка"
        ordering = ["user"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"],
                name="unique_user_following"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.following.username}"


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="favorite")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Избранные рецепты"
        verbose_name = "Избранный рецепт"
        ordering = ["user"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_favorite_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user} {self.recipe}"


class ShoppingCartRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="cart")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Рецепты в корзине"
        verbose_name = "Рецепт в корзине"
        ordering = ["user"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_shopping_cart_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user} {self.recipe}"
