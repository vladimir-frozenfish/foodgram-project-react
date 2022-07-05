from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework.relations import SlugRelatedField

from recipes.models import Ingredient, IngredientRecipe, FavoriteRecipe, User, Recipe, ShoppingCartRecipe, Tag, TagRecipe


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
                "email",
                "id",
                "username",
                "first_name",
                "last_name",
                "password",
                "is_subscribed"
            )
        model = User

    def get_is_subscribed(self, obj):
        """возвращает в поле is_subscribed True если текущий пользователь
        подписан на вызываемых в запросе GET"""
        request_user = self.context["request"].user
        if request_user.is_anonymous:
            return False
        following = [follower.following.username for follower in request_user.follower.all()]
        return obj.username in following

    def create(self, validated_data):
        """создание хэшируемого пароля"""
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, source='tag')
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorite",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time"
        )
        model = Recipe

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj.id)
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                {
                    "id": ingredient.ingredient.id,
                    "name": ingredient.ingredient.name,
                    "measurement_unit": ingredient.ingredient.measurement_unit,
                    "amount": ingredient.amount
                }
            )
        return ingredient_list

    def get_is_favorite(self, obj):
        """возвращает в поле is_vaforite True если текущий пользователь
        отметил рецепт в избранное"""
        request_user = self.context["request"].user
        if request_user.is_anonymous:
            return False
        favorite_recipes = [recipe.recipe.name for recipe in FavoriteRecipe.objects.filter(user=request_user.id)]
        return obj.name in favorite_recipes

    def get_is_in_shopping_cart(self, obj):
        """возвращает в поле is_in_shopping_cart True если текущий пользователь
        поместил рецепт в корзину"""
        request_user = self.context["request"].user
        if request_user.is_anonymous:
            return False
        recipes_in_shopping_cart = [recipe.recipe.name for recipe in ShoppingCartRecipe.objects.filter(user=request_user.id)]
        return obj.name in recipes_in_shopping_cart


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, source='tag', required=False)
    # ingredients = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), many=True, source='ingredient', required=False)
    # ingredients = serializers.ListField(many=True, source='ingredient', required=False)
    # ingredients = serializers.SerializerMethodField()
    # is_favorite = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            # "ingredients",
            # "is_favorite",
            # "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time"
        )
        model = Recipe


    def create(self, validated_data):
        # if 'tags' not in self.initial_data:
        #     recipe = Recipe.objects.create(**validated_data)
        #     return recipe
        #
        # tags = validated_data.pop('tag')
        # recipe = Recipe.objects.create(**validated_data)
        #
        # for tag in tags:
        #     TagRecipe.objects.create(tag=tag, recipe=recipe)
        #
        # return recipe

        try:
            tags = validated_data.pop('tag')
        except:
            tags = []

        try:
            ingredients = validated_data.pop('ingredient')
        except:
            ingredients = []

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)

        print(ingredients)
        # for ingredient in ingredients:
        #     print(ingredient)

        return recipe
