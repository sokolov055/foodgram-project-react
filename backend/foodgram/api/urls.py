from rest_framework import routers
from django.urls import path, include

from users.views import CustomUserViewSet
from recipes.views import (
    IngredientsViewSet,
    TagViewSet,
    RecipeViewSet
)

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
