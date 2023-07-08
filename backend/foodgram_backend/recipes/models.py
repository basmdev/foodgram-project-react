from django.db import models

from users.models import CustomUser


class Ingredient(models.Model):
    """Модель ингридиента."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        db_index=True
    )
    unit = models.CharField(
        max_length=256,
        verbose_name='Еденицы измерения'
    )

    class Meta():
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'unit'],
                name='uq_name_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.unit}'
    

class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        verbose_name='Название',
        max_length=256,
        unique=True
    )
    color_hex = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(
        max_length=256,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=256,
    )
    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name='Изображение'
    )
    description = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    time = models.IntegerField(
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name