from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from users.models import Follow, User
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class UserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )


class ShowSubscriptionsSerializer(UserSerializer):
    """Сериализатор подписок."""

    recipes = SerializerMethodField()
    recipes_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
        )

    def validate(self, attrs):
        author = self.instance
        user = self.context.get("request").user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail="Подписка уже существует", code="existing_subscription"
            )
        if user == author:
            raise ValidationError(
                detail="Подписка на самого себя невозможна",
                code="self_subscription",
            )
        return attrs

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        serializer = DemoRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор связи ингредиентов с рецептом."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class ShowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(
        many=True, source="ingredient_amount"
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "text",
            "ingredients",
            "cooking_time",
            "image",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "text",
            "ingredients",
            "cooking_time",
            "image",
            "tags",
        )

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for ingredient_data in ingredients:
            ingredient_list.append(
                IngredientRecipe(
                    ingredient=ingredient_data.pop("id"),
                    amount=ingredient_data.pop("amount"),
                    recipe=recipe,
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        request = self.context.get("request", None)
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop("tags"))
        ingredients = validated_data.pop("ingredients")
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ShowRecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class DemoRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FavoritesCartBasicSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок и избранного."""

    def to_representation(self, instance):
        return DemoRecipeSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data

    def validate(self, data):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        recipe = data["recipe"]
        if self.model.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            raise serializers.ValidationError({"status": "Уже существует"})
        return data


class FavoriteSerializer(FavoritesCartBasicSerializer):
    """Сериализатор избранного."""

    model = Favorite

    class Meta:
        model = Favorite
        fields = (
            "user",
            "recipe",
        )


class ShoppingCartSerializer(FavoritesCartBasicSerializer):
    """Сериализатор списка покупок."""

    model = ShoppingCart

    class Meta:
        model = ShoppingCart
        fields = (
            "user",
            "recipe",
        )
