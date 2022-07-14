from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings

from recipes.models import (Ingredient,
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
from .filters import IngredientFilter, RecipeFilter
from .utils import shopping_cart_data
from .pagination import CustomPagination


class CreateDeleteViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """Вьюсет для создания и удаления"""
    pass


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserOrReadAndCreate]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(url_path="me",
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def me(self, request):
        serializer = self.get_serializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(permission_classes=(permissions.IsAuthenticated,), detail=False)
    def subscriptions(self, request):
        follower = self.request.user.subscription.all()

        page = self.paginate_queryset(follower)
        serializer = SubscriptionUserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(["post"],
            url_path="set_password",
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def set_password(self, request, *args, **kwargs):
        request.data["current_user"] = request.user
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request,
                                                         context).send(to)

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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
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
        data = shopping_cart_data(request.user)

        filename = 'cart.txt'
        cart_text = open(filename, 'w')
        cart_text.write(data)

        response = HttpResponse(data,
                                content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response


class SubscribeViewSet(CreateDeleteViewSet):
    serializer_class = SubscribeSerializer

    def perform_create(self, serializer):
        follow_id = self.kwargs.get("user_id")
        follow = get_object_or_404(User, id=follow_id)
        serializer.save(user=self.request.user, following=follow)

    @action(methods=['delete'],
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def delete(self, request, *args, **kwargs):
        follow_id = self.kwargs.get("user_id")
        follow = get_object_or_404(User, id=follow_id)

        queryset = Subscribe.objects.filter(user=self.request.user,
                                            following=follow)
        if not queryset:
            return Response(
                {"message": "Ошибка отписки, возможно "
                            "вы на этого автора и небыли подписаны"},
                status=status.HTTP_400_BAD_REQUEST
            )
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

    @action(methods=['delete'],
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get("recipe_id")
        recipe = get_object_or_404(Recipe, id=recipe_id)

        queryset = FavoriteRecipe.objects.filter(user=self.request.user,
                                                 recipe=recipe)
        if not queryset:
            return Response(
                {"message": "Ошибка удаления рецепта из избранного, "
                            "возможно рецепта и не было в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
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

    @action(methods=['delete'],
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get("recipe_id")
        recipe = get_object_or_404(Recipe, id=recipe_id)

        queryset = ShoppingCartRecipe.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if not queryset:
            return Response(
                {"message": "Ошибка удаления рецепта из корзины, "
                            "возможно рецепта и не было в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
