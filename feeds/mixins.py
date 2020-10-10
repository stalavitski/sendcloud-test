from django.db.models import QuerySet

from feeds.models import FeedSubscription


class FeedSubscriptionViewMixin:
    """
    Mixin to provide drf-yasg valid QuerySet for FeedSubscription views.
    """
    def get_queryset(self) -> QuerySet:
        """
        Get FeedSubscription QuerySet owned by current user.

        :return: FeedSubscription QuerySet owned by current user.
        """
        if getattr(self, 'swagger_fake_view', False):
            # Queryset just for schema generation metadata
            return FeedSubscription.objects.none()

        return FeedSubscription.objects.filter(owner=self.request.user)
