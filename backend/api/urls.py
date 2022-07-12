from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet,
                    UserViewSet,
                    RecipeViewSet,
                    RecipeFavoriteViewSet,
                    TagViewSet,
                    SubscribeViewSet,
                    RecipeShoppingCartViewSet)


app_name = "api"

router = routers.DefaultRouter()

router.register("users", UserViewSet, basename="users")
router.register(r"users/(?P<user_id>\d+)/subscribe",
                SubscribeViewSet,
                basename="subscribe")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients",
                IngredientViewSet,
                basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register(r"recipes/(?P<recipe_id>\d+)/favorite",
                RecipeFavoriteViewSet,
                basename="favorite")
router.register(r"recipes/(?P<recipe_id>\d+)/shopping_cart",
                RecipeShoppingCartViewSet,
                basename="shopping_cart")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken"))
]
