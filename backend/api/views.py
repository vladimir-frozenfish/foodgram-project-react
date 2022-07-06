from djoser import views

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Ingredient, User, Recipe, Tag
from .serializers import IngredientSerializer, RecipeSerializer, RecipeCreateSerializer, TagSerializer, UserSerializer
from .permissions import IsUserOrReadAndCreate, IsAuthorOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserOrReadAndCreate]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(url_path="me",
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def get_mixin(self, request):
        serializer = self.get_serializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    # serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
