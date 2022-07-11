from collections import defaultdict

from recipes.models import IngredientRecipe


def shopping_cart_data(user):
    """функция возвращает информацию в виде строк о
    необходимых ингериеднтах рецептов, которые добавлены в корзину"""

    """переменные для формирования текстового файла"""
    recipes_name = set()
    ingredient_dict = defaultdict(int)

    shopping_cart_recipes = user.shopping_cart_recipe.all()
    for recipe in shopping_cart_recipes:
        recipes_name.add(recipe.name)
        ingredients = IngredientRecipe.objects.filter(recipe=recipe)
        for ingredient in ingredients:
            ingredient_dict[
                f'{ingredient.ingredient.name}, {ingredient.ingredient.measurement_unit}'] += ingredient.amount

    data = (f'Ваши рецепты: {", ".join(list(recipes_name))}\n'
            f'Необходимые ингредиенты для всех рецептов:\n')
    for ingredient, amount in ingredient_dict.items():
        ingredient, measurement_unit = ingredient.split(', ')
        data += f'- {ingredient}: {amount} {measurement_unit}\n'

    return data