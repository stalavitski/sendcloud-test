from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate

from feeds.views import FeedItemViewSet
from rss.tests import BaseTestCase


class FeedItemViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        """
        Set self.user before tests.
        """
        self.set_user()
        self.set_feed_subscription()
        self.set_feed()
        self.set_feed_item()

    # set_is_read tests
    def _get_set_is_read_response(self) -> Response:
        """
        Makes authenticated request to FeedItemViewSet.set_is_read
        and returns response.

        :return: Response for FeedItemViewSet.set_is_read.
        """
        factory = APIRequestFactory()
        view = FeedItemViewSet.as_view({'patch': 'set_is_read'})
        request = factory.patch('/feeds/items/', format='json')
        force_authenticate(request, user=self.user)
        return view(request, pk=self.feed_item.id)

    def test__set_is_read__update_value__on_unread_item(self) -> None:
        old_value = self.feed_item.is_read

        response = self._get_set_is_read_response()
        self.feed_item.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(old_value, self.feed_item.is_read)

    def test__set_is_read__dont_update_value__on_read_item(self) -> None:
        self.feed_item.is_read = True
        self.feed_item.save()
        old_value = self.feed_item.is_read

        response = self._get_set_is_read_response()
        self.feed_item.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(old_value, self.feed_item.is_read)
