from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.conf import settings
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient,
                            IngredientRecipe,
                            FavoriteRecipe,
                            User,
                            Recipe,
                            ShoppingCartRecipe,
                            Tag,
                            TagRecipe,
                            Subscribe)


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
        return Subscribe.objects.filter(user=request_user, following=obj).exists()

    def create(self, validated_data):
        """создание хэшируемого пароля"""
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user = self.initial_data["current_user"] or self.user
        assert user is not None

        try:
            validate_password(attrs["new_password"], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return super().validate(attrs)


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {
        "invalid_password": settings.CONSTANTS.messages.INVALID_PASSWORD_ERROR
    }

    def validate_current_password(self, value):
        is_password_valid = self.initial_data["current_user"].check_password(value)
        if is_password_valid:
            return value
        self.fail("invalid_password")


class SetPasswordSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass


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
    tags = TagSerializer(many=True, source='tag', required=False)
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
        return FavoriteRecipe.objects.filter(user=request_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """возвращает в поле is_in_shopping_cart True если текущий пользователь
        поместил рецепт в корзину"""
        request_user = self.context["request"].user
        if request_user.is_anonymous:
            return False
        return ShoppingCartRecipe.objects.filter(user=request_user, recipe=obj).exists()


class IngredientJSONField(serializers.Field):
    def to_representation(self, value):
        ingredients = value.all()
        for ingredient in ingredients:
            pass
        return {"Ингредиенты": "Пусто!"}

    def to_internal_value(self, data):
        return data


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, source='tag', required=False)
    ingredients = IngredientJSONField(required=False, source='ingredient')
    image = Base64ImageField(required=False)

    class Meta:
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time"
        )
        model = Recipe

    def create(self, validated_data):
        try:
            tags = validated_data.pop('tag')
        except:
            raise serializers.ValidationError(
                {"message": "Назначьте тэги для рецепта"}
            )

        try:
            ingredients = validated_data.pop('ingredient')
        except:
            raise serializers.ValidationError(
                {"message": "Добавьте ингредиенты для нового рецепта"}
            )

        recipe = Recipe.objects.create(**validated_data)
        TagRecipe.objects.bulk_create([TagRecipe(tag=tag, recipe=recipe) for tag in tags])
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                    amount=ingredient['amount']
                ) for ingredient in ingredients
            ]
        )
        return recipe


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """сериализатор для вывода рецептов при получении списка подписчиков"""
    class Meta:
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
        )
        model = Recipe


class SubscriptionUserSerializer(serializers.ModelSerializer):
    """сериализатор для вывода юзеров на которых подписан текущий пользователь"""
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')
    recipes = RecipeSubscribeSerializer(many=True)

    class Meta:
        fields = (
                "email",
                "id",
                "username",
                "first_name",
                "last_name",
                "is_subscribed",
                "recipes",
                "recipes_count"
            )
        model = User

    def get_is_subscribed(self, obj):
        return True


class SubscribeSerializer(serializers.ModelSerializer):
    """сериализатор для подписки на юзера"""
    user = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        fields = ("user", "following")
        model = Subscribe

    def validate(self, data):
        user = self.context["request"].user
        follow_id = self.context["view"].kwargs.get(["user_id"][0])
        follow = get_object_or_404(User, id=follow_id)

        if (self.context["request"].method == "POST"
                 and Subscribe.objects.filter(user=user, following=follow).exists()):
             raise serializers.ValidationError(
                 {"message": "Вы уже подписаны на этого пользователя"}
             )

        if self.context["request"].method == "POST" and user == follow:
             raise serializers.ValidationError(
                 {"message": "На самого себя нельзя подписаться"}
             )
        return data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """сериализатор для добавления рецепта в избранное"""
    user = UserSerializer(read_only=True)
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        fields = ("user", "recipe")
        model = FavoriteRecipe

    def validate(self, data):
        user = self.context["request"].user
        recipe_id = self.context["view"].kwargs.get(["recipe_id"][0])
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if (self.context["request"].method == "POST"
                 and FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists()):
             raise serializers.ValidationError(
                 {"message": "Вы уже добавили этот рецепт в избранное"}
             )

        return data


class RecipeShoppingCartSerializer(serializers.ModelSerializer):
    """сериализатор для добавления рецепта в корзину"""
    user = UserSerializer(read_only=True)
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        fields = ("user", "recipe")
        model = ShoppingCartRecipe

    def validate(self, data):
        user = self.context["request"].user
        recipe_id = self.context["view"].kwargs.get(["recipe_id"][0])
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if (self.context["request"].method == "POST"
                 and ShoppingCartRecipe.objects.filter(user=user, recipe=recipe).exists()):
             raise serializers.ValidationError(
                 {"message": "Вы уже добавили этот рецепт в корзину"}
             )

        return data



