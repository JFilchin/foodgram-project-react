import base64
import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Cart, Ingredient, IngredientsAmount, Recipe, Tag, FavoriteRecipe
from users.models import Subscription, User
from .validators import RecipeValidator


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для ингредиентов.'''
    name = serializers.ReadOnlyField(source='title')
    measurement_unit = serializers.ReadOnlyField(source='measure_unit')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для тегов.'''
    name = serializers.ReadOnlyField(source='title')

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class AmountIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор промежуточной модели кол-ва ингридиентов.'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount')


class IngredientsListSerializer(serializers.ModelSerializer):
    '''Сериализатор с полным списком полей ингредиентов.'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.title')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measure_unit'
    )

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateUserSerializer(UserCreateSerializer):
    '''Сериализатор для создания пользователя.'''

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class CustomUserSerializer(UserSerializer):
    '''Сериализатор для  пользователя.'''
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.author.filter(author=request.user).exists()


class ListOfRecipesSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для получения списка рецептов.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    '''
    name = serializers.CharField(source='title')
    text = serializers.CharField(source='description')
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        '''Получает ингредиенты из модели IngredientsAmount.'''
        ingredients = IngredientsAmount.objects.filter(recipe=obj)
        return IngredientsListSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        '''Показывать только рецепты, находящиеся в списке избранного.'''
        request = self.context['request'].user
        if request.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request,
            recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        '''Показывать только рецепты, находящиеся в списке покупок.'''
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.user_cart.filter(recipe=obj).exists()


class CreateUpdateRecipesSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания и обновления рецептов.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    '''
    name = serializers.CharField(source='title')
    text = serializers.CharField(source='description')
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, fields):
        '''Валидация полей рецепта.'''
        if not 'ingredients' in fields:
            raise serializers.ValidationError(
                'Поле ingredients не может быть пустым'
            )
        if not 'tags' in fields:
            raise serializers.ValidationError(
                'Поле tags не может быть пустым'
            )
        self.name = RecipeValidator.validate_name(fields['title'])
        self.ingredients = RecipeValidator.validate_ingredients(
            fields['ingredients']
        )
        self.tags = RecipeValidator.validate_tags(fields['tags'])
        self.cooking_time = RecipeValidator.validate_cooking_time(
            fields['cooking_time']
        )
        return fields

    @staticmethod
    def add_ingredients(recipe, ingredients):
        '''Добавляет ингредиенты.'''
        IngredientsAmount.objects.bulk_create([
            IngredientsAmount(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ])

    def create(self, validated_data):
        '''Метод создания рецепта.'''
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        '''Метод обновления рецепта.'''
        old_recipe = instance
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get(
            'description',
            instance.description
        )
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)

        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        IngredientsAmount.objects.filter(recipe=old_recipe).delete()
        self.add_ingredients(instance, ingredients)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=current_user,
            recipe=obj.id).exists()

    def to_representation(self, instance):
        return ListOfRecipesSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShortlistRecipesSerializer(serializers.ModelSerializer):
    '''Сериализатор короткого списка рецептов.'''
    name = serializers.CharField(source='title')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionOfUserSerializer(CustomUserSerializer):
    '''Сериализатор отображения подписок.'''

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        '''Отображение рецепта в подписках.'''
        request = self.context['request']
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        serializer = ShortlistRecipesSerializer(
            recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        '''Кол-во подписок.'''
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    '''Сериализатор для модели Subscription.'''

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на этого автора!'
            )
        ]

    def validate(self, data):
        '''Функция проверяет подписку на себя.'''
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя!'
            )
        return data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для Избранного.'''

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном!'
            )
        ]


class CartSerializer(serializers.ModelSerializer):
    '''Сериализатор для Корзины.'''

    class Meta:
        model = Cart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавляли это рецепт в список покупок'
            )
        ]
