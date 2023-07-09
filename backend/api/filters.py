from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe

User = get_user_model()


class CustomIngredientFilter(SearchFilter):
    """Фильтр ингредиента."""

    search_param = "name"

    class Meta:
        model = Ingredient
        fields = ("name",)


class CustomRecipeFilter(FilterSet):
    """Фильтр рецепта."""

    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method="custom_if_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(method="custom_if_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def custom_if_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.select_related("favorites__user").filter(
                favorites__user=self.request.user
            )
        return queryset

    def custom_if_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.select_related("shopping_list__user").filter(
                shopping_list__user=self.request.user
            )
        return queryset
