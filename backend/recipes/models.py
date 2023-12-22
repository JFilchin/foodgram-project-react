from colorfield.fields import ColorField
from django.core.validators import RegexValidator
from django.db import models
from users.models import User


class Recipe(models.Model):
    '''Модель рецепта.'''
    title = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    description = models.TextField(
        max_length=2000,
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientsAmount',
        verbose_name='Ингредиент'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    time_update = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='tags',
        verbose_name='Тег'
    )
    image = models.ImageField(upload_to='recipes/%Y/%m/%d/')

    class Meta:
        ordering = ('-time_create', '-time_update')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.title


class Tag(models.Model):
    '''Модель тега.'''
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тэга'
    )
    color = ColorField(
        max_length=7,
        verbose_name='Цветовой код в формате #49B64E'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Допускаются латинские буквы, цифры и _ '
        )],
        verbose_name='Уникальный идентификатор'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.title


class Ingredient(models.Model):
    '''Модель ингредиента.'''
    title = models.CharField(
        max_length=100,
        verbose_name='Название ингредиента'
    )
    measure_unit = models.CharField(
        max_length=100,
        verbose_name='Единица изменения'
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.title} {self.measure_unit}'


class IngredientsAmount(models.Model):
    '''Модель кол-ва ингредиентов в рецепте.'''
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Кол-во ингрeдиентов в рецепте'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_to_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Кол-во ингрeдиентов в рецепте'
        verbose_name_plural = 'Кол-во ингрeдиентов в рецепте'

    def __str__(self) -> str:
        return f'{self.ingredient} {self.amount}'


class FavoriteRecipe(models.Model):
    '''Модель избранных рецептов'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранное'
    )

    class Meta:
        verbose_name = 'Избранное'

    def __str__(self) -> str:
        return f'{self.user} {self.recipe}'


class Cart(models.Model):
    '''Модель корзины пользователя.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self) -> str:
        return f'{self.user} {self.recipe}'
