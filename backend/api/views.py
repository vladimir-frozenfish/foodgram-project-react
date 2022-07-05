from rest_framework import viewsets, permissions

from recipes.models import Ingredient, User, Recipe, Tag
from .serializers import IngredientSerializer, RecipeSerializer, RecipeCreateSerializer, TagSerializer, UserSerializer
from .permissions import IsUserOrReadAndCreate, IsAuthorOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserOrReadAndCreate]
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
