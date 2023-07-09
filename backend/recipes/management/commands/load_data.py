import json

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

INGREDIENTS_JSON_PATH = "../data/ingredients.json"


class Command(BaseCommand):
    help = "Загрузка ингредиентов"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Загрузка начата"))
        try:
            with open(INGREDIENTS_JSON_PATH, encoding="utf-8") as data_file_ingredients:
                ingredient_data = json.load(data_file_ingredients)
                for ingredients in ingredient_data:
                    Ingredient.objects.get_or_create(**ingredients)
        except (FileNotFoundError, json.JSONDecodeError, ValidationError) as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при загрузке: {e}"))

        self.stdout.write(self.style.SUCCESS("Загрузка завершена"))
