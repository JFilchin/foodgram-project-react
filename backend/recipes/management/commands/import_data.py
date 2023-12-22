import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Команда для импорта ингредиентов и тегов из CSV в базу данных'

    def handle(self, *args, **kwargs):
        with open(
            f'{getattr(settings, "CSV_DATA_ROOT")}/ingredients.csv',
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
            Ingredient.objects.all().delete()
            Ingredient.objects.bulk_create(ingredients)
        print('Импорт ингредиентов из CSV завершен.')
        with open(
            f'{getattr(settings, "CSV_DATA_ROOT")}/tags.csv',
            encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            tags = [
                Tag(
                    title=row[0],
                    color=row[1],
                    slug=row[2],
                )
                for row in reader
            ]
            Tag.objects.all().delete()
            Tag.objects.bulk_create(tags)
        print('Импорт тегов из CSV завершен.')
