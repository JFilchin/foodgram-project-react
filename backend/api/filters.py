from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    '''Фильтр по названию ингредиента.'''
    name = filters.CharFilter(
        field_name='title', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    '''
    Фильтр рецепта.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    '''
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    author = filters.AllValuesMultipleFilter(
        field_name='author__id'
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipe_in_cart__user=user)
        return queryset
