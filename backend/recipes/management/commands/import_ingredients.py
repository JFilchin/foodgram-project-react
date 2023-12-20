import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Команда для импорта ингредиентов из CSV в базу данных'

    def handle(self, *args, **kwargs):
        with open(
            f'{getattr(settings, "CSV_INGREDIENTS_ROOT")}/ingredients.csv',
            encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            ingredients = [
                Ingredient(
                    title=row[0],
                    measure_unit=row[1],
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients)
        print('Импорт завершен.')
