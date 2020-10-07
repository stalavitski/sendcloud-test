from typing import TYPE_CHECKING

from rest_framework import permissions
from rest_framework.request import Request

if TYPE_CHECKING:
    from feeds.models import FeedSubscription
    from feeds.views import FeedSubscriptionViewSet


class FeedSubscriptionPermission(permissions.BasePermission):
    def has_permission(
            self,
            request: Request,
            view: 'FeedSubscriptionViewSet'
    ) -> bool:
        """
        Check if user is authenticated.

        :param request: Request as a context to get current user.
        :param view: 'FeedSubscriptionViewSet',
        :return: Is user authenticated.
        """
        print(request, view)
        return request.user.is_authenticated

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
