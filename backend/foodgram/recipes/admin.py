from django.contrib import admin
from django.contrib.admin import display
from recipes.models import (Tag,
                            Recipe,
                            Ingredient,
                            RecipeIngredient,
                            FavoriteRecipe,
                            ShoppingList,
                            )


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_in_favorites')
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tags',)
    inlines = (RecipeIngredientInline, )

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс настройки раздела рецептов, которые добавлены в список покупок."""

    list_display = (
        'pk',
        'user',
        'recipe',
    )

    empty_value_display = 'значение отсутствует'
    list_editable = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)
