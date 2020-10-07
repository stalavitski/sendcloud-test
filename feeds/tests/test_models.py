from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from feeds.models import Feed, FeedItem, FeedSubscription

User = get_user_model()


class BaseFeedTestCase(TestCase):
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


class FeedSubscriptionTestCase(BaseFeedTestCase):
    def setUp(self) -> None:
        """
        Set self.user and self.feed_subscription before tests.
        """
        self.set_user()
        self.set_feed_subscription()

    # clean tests
    def test__clean__validation_error__on_unique_violation(self) -> None:
        message = 'Subscription to this feed is already exists.'
        feed_subscription = FeedSubscription(
            owner=self.user,
            url=self.feed_subscription.url
        )

        with self.assertRaisesMessage(ValidationError, message):
            feed_subscription.clean()

    def test__clean__success__on_same_owner_and_new_url(self) -> None:
        feed_subscription = FeedSubscription(
            owner=self.user,
            url='http://test2.com'
        )

        try:
            feed_subscription.clean()
        except ValueError:
            self.fail('clean() raised ExceptionType unexpectedly.')

    def test__clean__success__on_same_url_and_new_owner(self) -> None:
        self.set_additional_user()
        feed_subscription = FeedSubscription(
            owner=self.additional_user,
            url='http://test.com'
        )

        try:
            feed_subscription.clean()
        except ValueError:
            self.fail('clean() raised ExceptionType unexpectedly.')

    def test__clean__success__on_new_url_and_owner(self) -> None:
        self.set_additional_user()
        feed_subscription = FeedSubscription(
            owner=self.additional_user,
            url='http://test2.com'
        )

        try:
            feed_subscription.clean()
        except ValueError:
            self.fail('clean() raised ExceptionType unexpectedly.')


class FeedItemTestCase(BaseFeedTestCase):
    def setUp(self) -> None:
        """
        Set self.user and self.feed_subscription before tests.
        """
        self.set_user()
        self.set_feed_subscription()
        self.set_feed()
        self.set_feed_item()

    # clean tests
    def test__clean__validation_error__on_unique_violation(self) -> None:
        message = 'Feed item with this title is already exists.'
        feed_item = FeedItem(
            feed=self.feed,
            title=self.feed_item.title
        )

        with self.assertRaisesMessage(ValidationError, message):
            feed_item.clean()

    def test__clean__success__on_same_feed_and_new_title(self) -> None:
        feed_item = FeedItem(
            feed=self.feed,
            title='test2'
        )

        try:
            feed_item.clean()
        except ValueError:
            self.fail('clean() raised ExceptionType unexpectedly.')

    def test__clean__success__on_same_title_and_new_feed(self) -> None:
        self.set_additional_user()
        self.set_additional_feed_subscription()
        self.set_additional_feed()
        feed_item = FeedItem(
            feed=self.additional_feed,
            title=self.feed_item.title
        )

        try:
            feed_item.clean()
        except ValueError:
            self.fail('clean() raised ExceptionType unexpectedly.')

    def test__clean__success__on_new__title_and_feed(self) -> None:
        self.set_additional_user()
        self.set_additional_feed_subscription()
        self.set_additional_feed()
        feed_item = FeedItem(
            feed=self.additional_feed,
            title='test2'
        )

        try:
            feed_item.clean()
        except ValueError:
            self.fail('clean() raised ExceptionType unexpectedly.')
