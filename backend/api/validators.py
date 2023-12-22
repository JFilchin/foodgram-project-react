from django.forms import ValidationError
from django.utils.deconstruct import deconstructible
from rest_framework import serializers
from django.conf import settings


@deconstructible
class UsernameValidator:
    '''Проверка имени пользователя.'''
    code = 'username_valid'

    def __init__(self, message=None):
        self.message = message if message else 'Не допускается имя "me".'

    def __call__(self, value):
        if value.lower() == 'me':
            raise ValidationError(self.message, code=self.code)


class RecipeValidator:
    '''Класс валидации рецепта.'''

    def validate_name(name):
        '''Проверяет кол-во символов поля name.'''
        if len(name) > settings.RECIPE_NAME_MAX_LEN:
            raise serializers.ValidationError(
                'Длина поля `name` превышает 200 символов')
        return name

    def validate_ingredients(ingredients):
        '''Проверяет поля ингредиента: наличие, кол-во и уникальность.'''
        if not ingredients:
            raise serializers.ValidationError('Поле не может быть пустым')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < settings.INGREDIENTS_MIN_AMOUNT:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
        unique_ingredients = tuple(
            ingredient['id'] for ingredient in ingredients)
        if len(ingredients) != len(set(unique_ingredients)):
            raise serializers.ValidationError('Поле должно быть уникальным')
        return ingredients

    def validate_tags(tags):
        '''Проверяет поля тега: наличие и уникальность.'''
        print(tags)
        if not tags:
            raise serializers.ValidationError('Поле не может быть пустым')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Поле должно быть уникальным')
        return tags

    def validate_cooking_time(cooking_time):
        '''Проверяет поля cooking_time: наличие и кол-во.'''
        if not cooking_time:
            raise serializers.ValidationError('Поле не может быть пустым')
        if int(cooking_time) < settings.COOKING_TIME_MIN:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 1'
            )
        return cooking_time
