from django.contrib import admin
from .models import Ingredient, IngredientsAmount, Recipe, Tag


class IngredientsAmountInline(admin.TabularInline):
    '''
    Кофигурация промежуточной модели кол-ва ингридиентов в рецепте в админке.
    '''
    model = IngredientsAmount
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    '''Кофигурация Ingredient в админке.'''
    list_display = ('title', 'measure_unit')
    list_filter = ('title',)
    search_fields = ('title',)
    inlines = (IngredientsAmountInline, )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    '''Кофигурация Recipe в админке.'''
    list_display = ('title', 'author', 'image',)
    list_filter = ('title', 'author', 'tags',)
    search_fields = ('title', 'author', 'tags',)
    inlines = (IngredientsAmountInline, )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    '''Кофигурация Tag в админке.'''
    list_display = ('title', 'slug', 'color')
