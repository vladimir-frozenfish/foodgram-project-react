from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter

from recipes.models import Recipe


class RecipeFilter(FilterSet):
    tag = CharFilter(field_name="tag__name")

    class Meta:
        model = Recipe
        fields = ["tag"]
