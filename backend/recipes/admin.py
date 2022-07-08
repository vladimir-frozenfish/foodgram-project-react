from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Ingredient, IngredientRecipe, FavoriteRecipe, Recipe, ShoppingCartRecipe, Subscribe, Tag, TagRecipe, User


class CustomUserModel(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "get_subscription",
        "get_favorite_recipe",
        "get_shopping_cart_recipe"
    )
    search_fields = ("username",)
    list_filter = ("username", "email")
    empty_value_display = "-пусто-"


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "text", "image", "cooking_time", "get_tag", "get_ingredient")


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "tag")


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "amount")


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("user", "following")


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


class ShoppingCartRecipeAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


admin.site.register(User, CustomUserModel)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingCartRecipe, ShoppingCartRecipeAdmin)
