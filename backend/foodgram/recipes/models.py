from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    name = models.CharField(max_length=200)
    cooking_time = models.PositiveIntegerField()
    text = models.TextField()
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=('Автор рецепта'),
        help_text='Автор рецепта',
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField('Ingredient',
                                         through='RecipeIngredient')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """Промежуточная модель связи тега и рецепта"""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Тег + рецепт'
        verbose_name_plural = 'Теги + рецепты'

    def __str__(self):
        return f'{self.tag} => {self.recipe}'


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель связи ингредиента и рецепта"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Рецепт + ингредиент'
        verbose_name_plural = 'Рецепты + ингредиенты'

    def __str__(self):
        return f'{self.recipe} => {self.ingredient}'


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=('Рецепт'),
        related_name='favorites',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=('Пользователь'),
        related_name='favorite',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном пользователя {self.user}'


class ShoppingList(models.Model):
    """Модель списка покупок"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=('Рецепт'),
        related_name='shopping_cart',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=('Пользователь'),
        related_name='shopping_cart',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_shopping_cart',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} у пользователя {self.user}'
