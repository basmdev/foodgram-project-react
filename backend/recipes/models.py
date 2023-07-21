from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200, db_index=True, unique=True, verbose_name="Название"
    )
    color = ColorField(
        max_length=7, format="hex", unique=True, verbose_name="Цвет"
    )
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Адрес")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name[:35]


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=128, db_index=True, verbose_name="Название"
    )
    measurement_unit = models.CharField(
        max_length=128, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"[:35]


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Тег"
    )
    name = models.CharField(max_length=128, verbose_name="Название")
    image = models.ImageField(
        upload_to="recipes/image/", verbose_name="Изображение"
    )
    text = models.TextField(verbose_name="Рецепт")
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message="Время приготовления должно быть больше 0"
            )
        ],
        verbose_name="Время приготовления",
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe", verbose_name="Ингредиенты"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name[:35]


class IngredientRecipe(models.Model):
    """Модель ингредиентов рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_amount",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Ингредиентов должно быть больше 0")
        ],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Количество"
        verbose_name_plural = "Количество"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "ingredient",
                    "recipe",
                ),
                name="uq_recipe_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.ingredient.name}, {self.recipe.name}"[:35]


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        default_related_name = "favorites"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="uq_user_recipe",
            )
        ]

    def __str__(self):
        return f"{self.recipe}, {self.user}"[:35]


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_list",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        default_related_name = "shopping_list"

    def __str__(self):
        return f"{self.user}, {self.recipe}"[:35]
