from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet

from recipes.models import Cart, FavoriteRecipe, Ingredient, Recipe, Tag
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnlyPermission
from .pagination import CustomPagination
from .serializers import (
    CustomUserSerializer,
    CreateUpdateRecipesSerializer,
    IngredientSerializer,
    ListOfRecipesSerializer,
    TagSerializer,
    ShortlistRecipesSerializer,
    SubscriptionOfUserSerializer,
    SubscriptionSerializer
)
from .utils import download_recipe


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет для игредиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет для тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вьюсет для рецептов.'''
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListOfRecipesSerializer
        return CreateUpdateRecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=('POST', 'DELETE'),
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        '''Функция для добавления и удаления рецепта в/из избранные.'''
        user = self.request.user
        if request.method == 'POST':
            favorite_recipe = FavoriteRecipe.objects.filter(
                recipe__id=pk, user=user
            )
            if favorite_recipe.exists():
                return Response(
                    {'error': 'Рецепт уже есть в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Рецепт не существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = ShortlistRecipesSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Рецепт не существует.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            favorite_recipe = FavoriteRecipe.objects.filter(
                recipe__id=pk, user=user
            )
            if favorite_recipe.exists():
                favorite_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': ('Рецепт еще не добавлен в избранное.')},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        '''Функция добавления рецепта в список покупок.'''
        if request.method == 'POST':
            return self.add_to_cart(Cart, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_from_cart(Cart, request.user, pk)

    def add_to_cart(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже в корзине.'},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не существует.'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortlistRecipesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_cart(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        cart = model.objects.filter(user=user, recipe=recipe)
        if cart.exists():
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепта уже нет в вашей корзине.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        '''Функция скачивания рецептов из списка покупок.'''
        user_cart = request.user
        if not user_cart.user_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipes_list = Recipe.objects.filter(
            recipe_in_cart__user=user_cart
        )
        response = download_recipe(recipes_list)
        return response


class UsersViewSet(UserViewSet):
    '''Вьюсет для пользователей.'''
    queryset = User.objects.all()
    pagination_class = CustomPagination

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,),
            url_name='subscriptions', url_path='subscriptions')
    def get_subscriptions(self, request):
        '''
        Возвращает пользователей, на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.
        '''
        authors = User.objects.filter(author__user=self.request.user)
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(
            queryset=authors, request=request
        )
        serializer = SubscriptionOfUserSerializer(
            paginated_queryset, context={'request': request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=('POST', 'DELETE',),
            permission_classes=(permissions.IsAuthenticated,),
            url_name='subscribe', url_path='subscribe')
    def get_subscribe(self, request, id):
        '''
        Функция позволяет текущему пользователю подписаться
        или отписаться от других пользователей.
        '''
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={
                    'user': request.user.id,
                    'author': author.id
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = SubscriptionOfUserSerializer(
                author,
                context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE' and not subscription.exists():
            raise exceptions.ValidationError(
                'Вы уже подписаны на данного автора.'
            )
        if request.method == 'DELETE':
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=(permissions.IsAuthenticated,)
            )
    def get_me(self, request):
        '''Текущий пользователь.'''
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
