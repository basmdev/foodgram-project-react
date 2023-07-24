from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "color",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "name",
        "text",
        "cooking_time",
        "pub_date",
    )
    search_fields = (
        "name",
        "author",
        "tags",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-"
    inlines = (IngredientInline,)

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("ingredients", "tags")
        )
        return queryset


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = ("user",)
    list_filter = ("user",)
    empty_value_display = "-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("recipe")
        return queryset


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = ("user",)
    list_filter = ("recipe",)
    empty_value_display = "-"

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("recipe")
        return queryset
