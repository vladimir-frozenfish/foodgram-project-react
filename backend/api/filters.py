from django_filters.rest_framework import CharFilter, FilterSet, filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    tags = CharFilter(field_name="tag__slug")
    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ["tag", "author", "is_favorited", "is_in_shopping_cart"]

    def filter_is_favorited(self, queryset, value, obj):
        if obj:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value, obj):
        if obj:
            return queryset.filter(cart__user=self.request.user)
        return queryset

class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr="icontains")

    class Meta:
        model = Ingredient
        fields = ['name',]


