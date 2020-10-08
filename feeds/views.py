from django.db.models import QuerySet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from feeds.models import Feed, FeedSubscription
from feeds.permissions import FeedPermission, FeedSubscriptionPermission
from feeds.serializers import FeedSerializer, FeedSubscriptionSerializer


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
        return Feed.objects.filter(subscription__owner=self.request.user)
