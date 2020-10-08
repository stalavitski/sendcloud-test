from typing import TYPE_CHECKING

from rest_framework import permissions
from rest_framework.request import Request

if TYPE_CHECKING:
    from feeds.models import Feed, FeedSubscription
    from feeds.views import FeedSubscriptionViewSet, FeedViewSet


class FeedSubscriptionPermission(permissions.IsAuthenticated):
    def has_object_permission(
            self,
            request: Request,
            view: 'FeedSubscriptionViewSet',
            obj: 'FeedSubscription'
    ) -> bool:
        """
        Check if current user is an owner to a FeedSubscription.

        :param request: Request as a context to get current user.
        :param view: FeedSubscriptionViewSet.
        :param obj: FeedSubscription object to check.
        :return: Is user an owner.
        """
        return obj.owner == request.user


class FeedPermission(permissions.IsAuthenticated):
    def has_object_permission(
            self,
            request: Request,
            view: 'FeedViewSet',
            obj: 'Feed'
    ) -> bool:
        """
        Check if current user is an owner to a Feed.

        :param request: Request as a context to get current user.
        :param view: FeedViewSet.
        :param obj: Feed object to check.
        :return: Is user an owner.
        """
        return request.user and obj.subscription.owner_id == request.user.id
