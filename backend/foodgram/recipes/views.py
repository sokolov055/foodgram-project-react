from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import RecipeFilter, IngredientFilter
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from rest_framework.permissions import IsAuthenticated
from recipes.models import (Tag,
                            Recipe,
                            Ingredient,
                            FavoriteRecipe,
                            ShoppingList,
                            RecipeIngredient,
                            )
from api.pagination import CustomPagination
from api.serializers import (TagSerializer,
                             RecipeSerializer,
                             IngredientSerializer,
                             RecipeGETSerializer,
                             RecipeShortSerializer,
                             )
from rest_framework.decorators import action


class TagViewSet(ModelViewSet):
    """Представление тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для создания обьектов класса Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeGETSerializer
    pagination_class = CustomPagination
    permission_classes = (
        IsAuthorOrReadOnly | IsAdminOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(FavoriteRecipe, request.user, pk)
        else:
            return self.delete_from(FavoriteRecipe, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingList, request.user, pk)
        else:
            return self.delete_from(ShoppingList, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipeSerializer


class IngredientsViewSet(ModelViewSet):
    """Представление ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
