from django.contrib.auth import get_user_model
from django.test import TestCase

from feeds.models import Feed, FeedItem, FeedSubscription

User = get_user_model()


class BaseTestCase(TestCase):
    def set_user(self) -> None:
        """
        Create and set User object to self.user.
        """
        self.user, _ = User.objects.get_or_create(
            email='test@email.com',
            password='test_password',
            username='test_username'
        )

    def set_additional_user(self) -> None:
        """
        Create and set User object to self.additional_user.
        """
        self.additional_user, _ = User.objects.get_or_create(
            email='test2@email.com',
            password='test2_password',
            username='test2_username'
        )

    def set_feed_subscription(self) -> None:
        """
        Create and set FeedSubscription object to self.feed_subscription.
        """
        self.feed_subscription, _ = FeedSubscription.objects.get_or_create(
            owner=self.user,
            url='http://test.com'
        )

    def set_additional_feed_subscription(self) -> None:
        """
        Create and set FeedSubscription object to
        self.additional_feed_subscription.
        """
        self.additional_feed_subscription, _ = (
            FeedSubscription.objects.get_or_create(
                owner=self.additional_user,
                url='http://test2.com'
            )
        )

    def set_feed(self) -> None:
        """
        Create and set Feed object to self.feed.
        """
        self.feed, _ = Feed.objects.get_or_create(
            subscription=self.feed_subscription,
            title='test'
        )

    def set_additional_feed(self) -> None:
        """
        Create and set Feed object to self.feed.
        """
        self.additional_feed, _ = Feed.objects.get_or_create(
            subscription=self.additional_feed_subscription,
            title='test2'
        )

    def set_feed_item(self) -> None:
        """
        Create and set FeedItem object to self.feed_item.
        """
        self.feed_item, _ = FeedItem.objects.get_or_create(
            feed=self.feed,
            title='test'
        )
