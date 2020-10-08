from typing import Dict, Tuple

from django.db.models import QuerySet
from django.http import Http404
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from feeds.models import Feed, FeedItem, FeedSubscription
from feeds.permissions import (
    FeedItemPermission,
    FeedPermission,
    FeedSubscriptionPermission
)
from feeds.serializers import (
    FeedItemSerializer,
    FeedSerializer,
    FeedSubscriptionSerializer
)


class FeedSubscriptionViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'delete', 'post']
    permission_classes = [FeedSubscriptionPermission]
    serializer_class = FeedSubscriptionSerializer

    def get_queryset(self) -> QuerySet:
        """
        Get FeedSubscription QuerySet owned by current user.

        :return: FeedSubscription QuerySet owned by current user.
        """
        return FeedSubscription.objects.filter(owner=self.request.user)


class FeedViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    http_method_names = ['get', 'head']
    permission_classes = [FeedPermission]
    serializer_class = FeedSerializer

    def get_queryset(self) -> QuerySet:
        """
        Get Feed QuerySet owned by current user.

        :return: Feed QuerySet owned by current user.
        """
        return (
            Feed
            .objects
            .prefetch_related('categories')
            .filter(subscription__owner=self.request.user)
        )


class FeedItemViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['feed', 'is_read']
    http_method_names = ['get', 'head', 'patch']
    ordering_fields = ['updated']
    permission_classes = [FeedItemPermission]
    serializer_class = FeedItemSerializer

    def get_queryset(self) -> QuerySet:
        """
        Get Feed QuerySet owned by current user.

        :return: Feed QuerySet owned by current user.
        """
        return (
            FeedItem
            .objects
            .prefetch_related('categories')
            .filter(feed__subscription__owner=self.request.user)
        )

    @action(detail=True, methods=['patch'], url_path='set-is-read')
    def set_is_read(
            self,
            request: Request,
            *args: Tuple,
            **kwargs: Dict
    ) -> Response:
        """
        Set is_read for unread FeedItem to True.

        :param request: Request with contextual information.
        :param args: Arguments.
        :param kwargs: Keyword arguments.
        :return: Response with 204 (No Content) status.
        """
        feed_item = self.get_object()

        if feed_item.is_read:
            raise Http404

        feed_item.is_read = True
        feed_item.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
