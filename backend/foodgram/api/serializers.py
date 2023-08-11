from djoser.serializers import UserCreateSerializer, UserSerializer
import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient
from users.models import Subscribe

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Создаёт пользователя"""
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            )

    def get_is_subscribed(self, object):
        """Проверяет, подписан ли текущий пользователь на автора аккаунта."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.author.filter(subscriber=request.user).exists()


class SubscribeSerializer(CustomUserSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('author', 'subscriber'),
                message='Вы уже подписывались на этого автора'
            )
        ]

    def validate(self, data):
        """Проверяем, что пользователь не подписывается на самого себя."""
        if data['subscriber'] == data['author']:
            raise serializers.ValidationError(
                'Подписка на cамого себя не имеет смысла'
            )
        return data


class SubscriptionShowSerializer(CustomUserSerializer):
    """Сериализатор отображения подписок."""

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
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, object):
        return object.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=False,
        allow_null=True
        )
    author = CustomUserSerializer(read_only=True)
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
            'cooking_time'
        )

    @staticmethod
    def get_ingredients(object):
        """Получает ингредиенты из модели IngredientAmount."""
        ingredients = RecipeIngredient.objects.filter(recipe=object)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, object):
        """Проверяет, добавил ли текущий пользователь рецепт в избанное."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        """Проверяет, добавил ли текущий пользователь
        рецепт в список покупок."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=object).exists()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
        )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField(use_url=True, max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def validate_ingredients(self, ingredients):
        """Проверяем, что рецепт содержит уникальные ингредиенты
        и их количество не меньше 1."""
        ingredients_data = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise serializers.ValidationError(
                'Ингредиенты рецепта должны быть уникальными'
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
        return ingredients

    def validate_tags(self, tags):
        """Проверяем, что рецепт содержит уникальные теги."""
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги рецепта должны быть уникальными'
            )
        return tags

    @staticmethod
    def add_ingredients(ingredients_data, recipe):
        """Добавляет ингредиенты."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=Ingredient.objects.get(
                    id=ingredient['ingredient'].id
                    ),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        ])

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        recipe = instance
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        instance.ingredients.clear()
        tags_data = validated_data.get('tags')
        instance.tags.set(tags_data)
        ingredients_data = validated_data.get('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients_data, recipe)
        instance.save()
        return instance

    def to_representation(self, recipe):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = RecipeGETSerializer(recipe)
        return serializer.data
