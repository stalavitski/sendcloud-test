from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from feeds.models import FeedItem, FeedSubscription
from rss.tests import BaseTestCase

User = get_user_model()


class FeedSubscriptionTestCase(BaseTestCase):
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


class FeedItemTestCase(BaseTestCase):
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
