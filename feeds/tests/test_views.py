from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate

from feeds.views import FeedItemViewSet, FeedSubscriptionViewSet
from rss.tests import BaseTestCase


class FeedSubscriptionViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        """
        Set self.user before tests.
        """
        self.set_user()
        self.set_feed_subscription()

    # retry tests
    def _get_retry_response(self) -> Response:
        """
        Makes authenticated request to FeedSubscription.retry
        and returns response.

        :return: Response for FeedSubscription.retry.
        """
        factory = APIRequestFactory()
        view = FeedSubscriptionViewSet.as_view({'patch': 'retry'})
        request = factory.patch('/feeds/subscriptions/', format='json')
        force_authenticate(request, user=self.user)
        return view(request, pk=self.feed_subscription.id)

    def test__retry__reset_stats__on_stopped_subscription(self) -> None:
        self.feed_subscription.retries = 5
        self.feed_subscription.is_stopped = True
        self.feed_subscription.save()
        old_retries = self.feed_subscription.retries
        old_is_stopped = self.feed_subscription.is_stopped

        response = self._get_retry_response()
        self.feed_subscription.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(old_retries, self.feed_subscription.retries)
        self.assertNotEqual(old_is_stopped, self.feed_subscription.is_stopped)

    def test__retry__dont_reset_stats__on_unstopped_subscription(self) -> None:
        old_retries = self.feed_subscription.retries
        old_is_stopped = self.feed_subscription.is_stopped

        response = self._get_retry_response()
        self.feed_subscription.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(old_retries, self.feed_subscription.retries)
        self.assertEqual(old_is_stopped, self.feed_subscription.is_stopped)


class FeedItemViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        """
        Set self.user before tests.
        """
        self.set_user()
        self.set_feed_subscription()
        self.set_feed()
        self.set_feed_item()

    # is_read tests
    def _get_is_read_response(self) -> Response:
        """
        Makes authenticated request to FeedItemViewSet.is_read
        and returns response.

        :return: Response for FeedItemViewSet.is_read.
        """
        factory = APIRequestFactory()
        view = FeedItemViewSet.as_view({'patch': 'is_read'})
        request = factory.patch('/feeds/items/', format='json')
        force_authenticate(request, user=self.user)
        return view(request, pk=self.feed_item.id)

    def test__is_read__update_value__on_unread_item(self) -> None:
        old_value = self.feed_item.is_read

        response = self._get_is_read_response()
        self.feed_item.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(old_value, self.feed_item.is_read)

    def test__is_read__dont_update_value__on_read_item(self) -> None:
        self.feed_item.is_read = True
        self.feed_item.save()
        old_value = self.feed_item.is_read

        response = self._get_is_read_response()
        self.feed_item.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(old_value, self.feed_item.is_read)
