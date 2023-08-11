from djoser.views import UserViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from api.pagination import CustomPagination
from users.models import User, Subscribe
from api.serializers import (CustomUserSerializer,
                             SubscribeSerializer,
                             SubscriptionShowSerializer,
                             )


class CustomUserViewSet(UserViewSet):
    """Представление пользователя"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_me(self, request):
        """Позволяет пользователю получить подробную информацию о себе
        и редактировать её."""
        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Позволяет текущему пользователю подписываться/отписываться от
        от автора контента, чей профиль он просматривает."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'subscriber': request.user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = SubscriptionShowSerializer(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            Subscribe, subscriber=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        """Возвращает авторов контента, на которых подписан
        текущий пользователь.."""
        authors = User.objects.filter(author__subscriber=request.user)
        paginator = CustomPagination()
        result_pages = paginator.paginate_queryset(
            queryset=authors, request=request
        )
        serializer = SubscriptionShowSerializer(
            result_pages, context={'request': request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)
