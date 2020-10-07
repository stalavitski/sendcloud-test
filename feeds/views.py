from django.db.models import QuerySet
from rest_framework.viewsets import ModelViewSet

from feeds.models import FeedSubscription
from feeds.permissions import FeedSubscriptionPermission
from feeds.serializers import FeedSubscriptionSerializer


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
