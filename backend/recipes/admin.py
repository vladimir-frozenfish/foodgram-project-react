from django.contrib import admin

from .models import Ingredient, Recipe, Tag, TagRecipe, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
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
    list_display = ("id", "name", "author", "text", "image", "cooking_time", "get_tag")


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "tag")


admin.site.register(User, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
