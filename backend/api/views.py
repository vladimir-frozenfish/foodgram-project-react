from collections import defaultdict

from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from djoser import signals, utils
from djoser.compat import get_user_email
from djoser.conf import settings

from recipes.models import (Ingredient,
                            IngredientRecipe,
                            FavoriteRecipe,
                            User,
                            Recipe,
                            Tag,
                            Subscribe,
                            ShoppingCartRecipe)
from .serializers import (IngredientSerializer,
                          RecipeSerializer,
                          RecipeCreateSerializer,
                          RecipeFavoriteSerializer,
                          RecipeShoppingCartSerializer,
                          TagSerializer,
                          UserSerializer,
                          SetPasswordSerializer,
                          SubscribeSerializer,
                          SubscriptionUserSerializer)
from .permissions import IsUserOrReadAndCreate, IsAuthorOrReadOnly
from .filters import RecipeFilter


class CreateDeleteViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """Вьюсет для создания и удаления"""
    pass


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserOrReadAndCreate]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(url_path="me", permission_classes=(permissions.IsAuthenticated,), detail=False)
    def me(self, request):
        serializer = self.get_serializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(permission_classes=(permissions.IsAuthenticated,), detail=False)
    def subscriptions(self, request):
        subscriptions = Subscribe.objects.filter(user=request.user)

        follower = []
        for subscribe in subscriptions:
            follower.append(subscribe.following)

        page = self.paginate_queryset(follower)
        serializer = SubscriptionUserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(["post"], url_path="set_password", permission_classes=(permissions.IsAuthenticated,), detail=False)
    def set_password(self, request, *args, **kwargs):
        request.data["current_user"] = request.user
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(permission_classes=(permissions.IsAuthenticated,), detail=False)
    def download_shopping_cart(self, request):
        """функция возвращает при api запросе текстовый файл со списком ингредиентов
        всех рецептов, которые были в корзине у аутентифицированного юзера"""

        """переменные для формирования текстового файла"""
        recipes_name = set()
        ingredient_dict = defaultdict(int)

        user = request.user
        shopping_cart_recipes = user.shopping_cart_recipe.all()
        for recipe in shopping_cart_recipes:
            recipes_name.add(recipe.name)
            ingredients = IngredientRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                ingredient_dict[f'{ingredient.ingredient.name}, {ingredient.ingredient.measurement_unit}'] += ingredient.amount

        data = (f'Ваши рецепты: {", ".join(list(recipes_name))}\n'
                f'Необходимые ингредиенты для всех рецептов:\n')
        for ingredient, amount in ingredient_dict.items():
            ingredient, measurement_unit = ingredient.split(', ')
            data += f'- {ingredient}: {amount} {measurement_unit}\n'

        filename = 'cart.txt'
        cart_text = open(filename, 'w')
        cart_text.write(data)

        response = HttpResponse(data, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response


class SubscribeViewSet(CreateDeleteViewSet):
    serializer_class = SubscribeSerializer

    def perform_create(self, serializer):
        follow_id = self.kwargs.get("user_id")
        follow = get_object_or_404(User, id=follow_id)
        serializer.save(user=self.request.user, following=follow)

    @action(methods=['delete'], permission_classes=(permissions.IsAuthenticated,), detail=False)
    def delete(self, request, *args, **kwargs):
        follow_id = self.kwargs.get("user_id")
        follow = get_object_or_404(User, id=follow_id)

        queryset = Subscribe.objects.filter(user=self.request.user, following=follow)
        if not queryset:
            return Response({"message": "Ошибка отписки, возможно вы на этого автора и небыли подписаны"}, status=status.HTTP_400_BAD_REQUEST)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeFavoriteViewSet(CreateDeleteViewSet):
    """Вьюсет для добавления и удаления рецепта из избранного
    для текущего пользователя"""
    serializer_class = RecipeFavoriteSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get("recipe_id")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

    @action(methods=['delete'], permission_classes=(permissions.IsAuthenticated,), detail=False)
    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get("recipe_id")
        recipe = get_object_or_404(Recipe, id=recipe_id)

        queryset = FavoriteRecipe.objects.filter(user=self.request.user, recipe=recipe)
        if not queryset:
            return Response({"message": "Ошибка удаления рецепта из избранного, возможно рецепта и не было в избранном"}, status=status.HTTP_400_BAD_REQUEST)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeShoppingCartViewSet(CreateDeleteViewSet):
    """Вьюсет для добавления и удаления рецепта из корзины
    для текущего пользователя"""
    serializer_class = RecipeShoppingCartSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get("recipe_id")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

    @action(methods=['delete'], permission_classes=(permissions.IsAuthenticated,), detail=False)
    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get("recipe_id")
        recipe = get_object_or_404(Recipe, id=recipe_id)

        queryset = ShoppingCartRecipe.objects.filter(user=self.request.user, recipe=recipe)
        if not queryset:
            return Response({"message": "Ошибка удаления рецепта из корзины, возможно рецепта и не было в корзине"}, status=status.HTTP_400_BAD_REQUEST)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
