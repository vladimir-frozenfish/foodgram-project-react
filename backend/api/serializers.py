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
        fields = ("email",
                  "id",
                  "username",
                  "first_name",
                  "last_name",
                  "password",
                  "is_subscribed")
        model = User

    def get_is_subscribed(self, obj):
        """возвращает в поле is_subscribed True если текущий пользователь
        подписан на вызываемых в запросе GET"""
        request_user = self.context["request"].user
        if request_user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request_user,
                                        following=obj).exists()

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
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )
        return super().validate(attrs)


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {
        "invalid_password": settings.CONSTANTS.messages.INVALID_PASSWORD_ERROR
    }

    def validate_current_password(self, value):
        is_password_valid = (
            self.initial_data["current_user"].check_password(value)
        )
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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
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

    def get_is_favorited(self, obj):
        """возвращает в поле is_vaforite True если текущий пользователь
        отметил рецепт в избранное"""
        request_user = self.context["request"].user
        if request_user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request_user,
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """возвращает в поле is_in_shopping_cart True если текущий пользователь
        поместил рецепт в корзину"""
        request_user = self.context["request"].user
        if request_user.is_anonymous:
            return False
        return ShoppingCartRecipe.objects.filter(
            user=request_user,
            recipe=obj).exists()


# class IngredientAmountSerializers(serializers.Serializer):
#      id = serializers.CharField()
#      amount = serializers.CharField()


class IngredientJSONField(serializers.Field):
    def to_representation(self, value):
        return value.all().values("id")

    def to_internal_value(self, data):
        # raise serializers.ValidationError({"message": "Количество должно быть больше нуля"})      # здесь не работает в react

        # ingr_id = []
        #     ingrs = data
        #
        #     for ingr in ingrs:
        #         # ingr_id.append(ingr["id"])
        #
        #         if int(ingr["amount"]) <= 0:
        #             continue
        #             # raise serializers.ValidationError(
        #             #     {"message": "Количество должно быть больше нуля"}
        #             # )

        # """проверка, чтобы не было двух или более одинаковых элементов"""
        # if len(ingredients_id) != len(set(ingredients_id)):
        #     raise serializers.ValidationError(
        #         {"message": "Одинаковых ингредиентов не должно быть"}
        #     )

        return data


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source='tag',
        required=False
    )
    # ingredients = IngredientAmountSerializers(required=True, source='ingredient', many=True)
    ingredients = IngredientJSONField(required=True, source='ingredient')
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

    def list_for_tags(self, recipe, tags):
        """возвращает список тэгов для создания или
        обновления рецепта"""
        return [TagRecipe(tag=tag, recipe=recipe) for tag in tags]

    def list_for_ingredients(self, recipe, ingredients):
        """возвращает список ингредиентов для создания или
        обновления рецепта"""
        return [IngredientRecipe(
            recipe=recipe,
            ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
            amount=ingredient['amount']
        ) for ingredient in ingredients]

    def chek_ingredients(self, ingredients):
        """функция проверяет введенные ингредиенты на дублирование
        и количество должно быть больше нуля
        Функция так названа, так как на фронтенде React если функцию назвать
        validate_ingredients - не работает"""
        ingredients_id = []

        for ingredient in ingredients:
            ingredients_id.append(ingredient["id"])

            if not ingredient["amount"].isnumeric() or int(ingredient["amount"]) <= 0:
                raise serializers.ValidationError(
                    {"message": "Количество должно быть числом больше нуля"}
                )
        """проверка, чтобы не было двух или более одинаковых элементов"""
        if len(ingredients_id) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                {"message": "Одинаковых ингредиентов не должно быть"}
            )

    def create(self, data):
        try:
            tags = data.pop('tag')
        except:
            raise serializers.ValidationError(
                {"message": "Назначьте тэги для рецепта"}
            )

        try:
            ingredients = data.pop('ingredient')
        except:
            raise serializers.ValidationError(
                {"message": "Добавьте ингредиенты для нового рецепта"}
            )

        self.chek_ingredients(ingredients)

        recipe = Recipe.objects.create(**data)
        TagRecipe.objects.bulk_create(self.list_for_tags(recipe, tags))
        IngredientRecipe.objects.bulk_create(
            self.list_for_ingredients(recipe, ingredients)
        )
        return recipe

    def update(self, instance, data):
        instance.image = data.get('image', instance.image)
        instance.name = data.get('name', instance.name)
        instance.text = data.get('text', instance.text)
        instance.cooking_time = data.get('cooking_time', instance.cooking_time)
        instance.save()

        """удаление страых тэгов и рецептов"""
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()

        """получение новых тэгов и рецептов и сохранение 
        их для измененного рецепта"""
        ingredients = data.get('ingredient')
        tags = data.get('tag')

        TagRecipe.objects.bulk_create(self.list_for_tags(instance, tags))
        IngredientRecipe.objects.bulk_create(
            self.list_for_ingredients(instance, ingredients)
        )
        return instance


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
    """сериализатор для вывода юзеров
    на которых подписан текущий пользователь"""
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')
    recipes = RecipeSubscribeSerializer(many=True)

    class Meta:
        fields = ("email",
                  "id",
                  "username",
                  "first_name",
                  "last_name",
                  "is_subscribed",
                  "recipes",
                  "recipes_count")
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
                and Subscribe.objects.filter(user=user,
                                             following=follow).exists()):
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
                and FavoriteRecipe.objects.filter(
                    user=user,
                    recipe=recipe).exists()):
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
                and ShoppingCartRecipe.objects.filter(
                    user=user,
                    recipe=recipe).exists()):
            raise serializers.ValidationError(
                {"message": "Вы уже добавили этот рецепт в корзину"}
            )

        return data
