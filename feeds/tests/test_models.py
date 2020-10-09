from django.conf import settings
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

    # failure tests
    def test__failure__increments_retries(self) -> None:
        old_retries = self.feed_subscription.retries

        self.feed_subscription.failure()
        self.feed_subscription.refresh_from_db()

        self.assertEqual(old_retries + 1, self.feed_subscription.retries)

    def test__failure__sets_is_stopped__if_retries_exceeded(self) -> None:
        self.feed_subscription.retries = settings.MAX_RETRIES - 1
        self.feed_subscription.save()

        self.feed_subscription.failure()
        self.feed_subscription.refresh_from_db()

        self.assertTrue(self.feed_subscription.is_stopped)

    def test__failure__is_not_stopped__if_retries_not_exceeded(self) -> None:
        self.feed_subscription.retries = settings.MAX_RETRIES - 2
        self.feed_subscription.save()

        self.feed_subscription.failure()
        self.feed_subscription.refresh_from_db()

        self.assertFalse(self.feed_subscription.is_stopped)

    def test__failure__set_status_to_ready(self) -> None:
        self.feed_subscription.status = FeedSubscription.STATUS_NEW
        self.feed_subscription.save()

        self.feed_subscription.failure()
        self.feed_subscription.refresh_from_db()

        self.assertEqual(
            self.feed_subscription.status,
            FeedSubscription.STATUS_READY
        )

    # in_progress tests
    def test__in_progress__set_status_to_in_progress(self) -> None:
        self.feed_subscription.status = FeedSubscription.STATUS_NEW
        self.feed_subscription.save()

        self.feed_subscription.in_progress()
        self.feed_subscription.refresh_from_db()

        self.assertEqual(
            self.feed_subscription.status,
            FeedSubscription.STATUS_IN_PROGRESS
        )

    # failure tests
    def test__success__resets_retries_and_is_stopped(self) -> None:
        self.feed_subscription.retries = settings.MAX_RETRIES
        self.feed_subscription.is_stopped = True
        self.feed_subscription.save()

        self.feed_subscription.success()
        self.feed_subscription.refresh_from_db()

        self.assertEqual(self.feed_subscription.retries, 0)
        self.assertFalse(self.feed_subscription.is_stopped)

    def test__success__set_status_to_ready(self) -> None:
        self.feed_subscription.status = FeedSubscription.STATUS_NEW
        self.feed_subscription.save()

        self.feed_subscription.success()
        self.feed_subscription.refresh_from_db()

        self.assertEqual(
            self.feed_subscription.status,
            FeedSubscription.STATUS_READY
        )


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
