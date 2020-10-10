from typing import Dict, Tuple

from django.db.models import QuerySet
from django.http import Http404
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from feeds.mixins import FeedSubscriptionViewMixin
from feeds.models import Feed, FeedItem, FeedSubscription
from feeds.permissions import (
    FeedItemPermission,
    FeedPermission,
    FeedSubscriptionPermission
)
from feeds.serializers import (
    FeedItemSerializer,
    FeedSerializer,
    FeedSubscriptionRetrySerializer,
    FeedSubscriptionSerializer
)
from feeds.tasks import update_feed


class FeedSubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    FeedSubscriptionViewMixin,
    GenericViewSet
):
    http_method_names = ['get', 'head', 'delete', 'post']
    permission_classes = [FeedSubscriptionPermission]
    serializer_class = FeedSubscriptionSerializer


class FeedSubscriptionRetryView(FeedSubscriptionViewMixin, UpdateAPIView):
    http_method_names = ['patch']
    model = FeedSubscription
    permission_classes = [FeedSubscriptionPermission]
    serializer_class = FeedSubscriptionRetrySerializer

    @swagger_auto_schema(
        operation_description='Force stopped feed update.',
        request_body=no_body
    )
    def patch(
            self,
            request: Request,
            *args: Tuple,
            **kwargs: Dict
    ) -> Response:
        """
        Update FeedSubscription to start update attempts after it has been
        stopped.

        :param request: Request with contextual information.
        :param args: Arguments.
        :param kwargs: Keyword arguments.
        :return: Response with 204 (No Content) status.
        """
        feed_subscription = self.get_object()

        if not feed_subscription.is_stopped:
            raise Http404

        # Reset is_stopped and retries values.
        feed_subscription.success()
        # Force update
        update_feed.delay(feed_subscription.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeedViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    http_method_names = ['get', 'head']
    permission_classes = [FeedPermission]
    serializer_class = FeedSerializer

    def get_queryset(self) -> QuerySet:
        """
        Get Feed QuerySet owned by current user.

        :return: Feed QuerySet owned by current user.
        """
        if getattr(self, 'swagger_fake_view', False):
            # Queryset just for schema generation metadata
            return Feed.objects.none()

        return (
            Feed
            .objects
            .prefetch_related('categories')
            .filter(subscription__owner=self.request.user)
        )


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description='(optional) Order feeds by created, pub_date '
                            'or updated.',
                type=openapi.TYPE_STRING
            )
        ]
    )
)
class FeedItemViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['feed', 'is_read']
    http_method_names = ['get', 'head', 'patch']
    ordering_fields = ['created', 'pub_date', 'updated']
    permission_classes = [FeedItemPermission]
    serializer_class = FeedItemSerializer

    def get_queryset(self) -> QuerySet:
        """
        Get Feed QuerySet owned by current user.

        :return: Feed QuerySet owned by current user.
        """
        if getattr(self, 'swagger_fake_view', False):
            # Queryset just for schema generation metadata
            return FeedItem.objects.none()

        return (
            FeedItem
            .objects
            .prefetch_related('categories')
            .filter(feed__subscription__owner=self.request.user)
        )

    @swagger_auto_schema(
        'patch',
        operation_description='Mark unread feed item as read.',
        request_body=no_body
    )
    @action(detail=True, methods=['patch'], url_path='is-read')
    def is_read(
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
