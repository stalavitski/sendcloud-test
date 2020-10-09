import vcr
from feedparser.util import FeedParserDict

from feeds.models import FeedCategory, FeedItemCategory, FeedSubscription
from feeds.utils.feedupdater import (
    FeedItemUpdater,
    FeedUpdater,
    FeedUpdaterDoesntExistError,
    FeedUpdaterInvalidRSSError, BaseFeedUpdater,
)
from datetime import datetime
from time import struct_time
from rss.tests import BaseTestCase


class BaseFeedUpdaterTestCase(BaseTestCase):
    # get_pub_date tests
    def test__get_pub_date__return_none__if_no_date(self) -> None:
        pub_date = BaseFeedUpdater.get_pub_date({})

        self.assertIsNone(pub_date)

    def test__get_pub_date__return_date__if_date_is_tuple(self) -> None:
        data = {
            'published_parsed': (2000, 11, 30, 0, 0, 0, 3, 335, 1)
        }

        pub_date = BaseFeedUpdater.get_pub_date(data)

        self.assertIsNotNone(pub_date)
        self.assertEqual(datetime(2000, 11, 30), pub_date)

    def test__get_pub_date__return_date__if_date_is_struct_time(self) -> None:
        data = {
            'published_parsed': struct_time((2000, 11, 30, 0, 0, 0, 3, 335, 1))
        }

        pub_date = BaseFeedUpdater.get_pub_date(data)

        self.assertIsNotNone(pub_date)
        self.assertEqual(datetime(2000, 11, 30), pub_date)


class FeedItemUpdaterTestCase(BaseTestCase):
    def setUp(self) -> None:
        """
        Set self.user before tests.
        """
        self.set_user()
        self.set_feed_subscription()
        self.set_feed()
        self.set_feed_item()

    # _get_feed tests
    def test__get_feed__raise__if_not_exists(self) -> None:
        with self.assertRaises(FeedUpdaterDoesntExistError):
            FeedItemUpdater._get_feed(0)

    def test__get_feed__return_feed__if_exists(self) -> None:
        feed = FeedItemUpdater._get_feed(self.feed.id)

        self.assertEqual(feed.id, self.feed.id)

    # _update_feed_item tests
    def test__update_feed_item__create_feed_item__if_not_exists(self) -> None:
        title = 'test2'
        data = {
            'title': title
        }

        feed_item = FeedItemUpdater._update_feed_item(self.feed, data)

        self.assertNotEqual(feed_item.id, self.feed_item.id)
        self.assertEqual(feed_item.title, title)

    def test__update_feed_item__update_feed_item__if_exists(self) -> None:
        guid = 'test'
        data = {
            'id': guid,
            'title': self.feed_item.title
        }

        FeedItemUpdater._update_feed_item(self.feed, data)
        self.feed_item.refresh_from_db()

        self.assertEqual(self.feed_item.guid, guid)

    # _update_categories tests
    def test__update_categories__replace_old_categories_with_new(self) -> None:
        FeedItemCategory.objects.create(
            item=self.feed_item,
            keyword='old_keyword'
        )
        new_keyword = 'keyword'
        data = {
            'tags': [{
                'term': 'keyword',
            }]
        }

        FeedItemUpdater._update_categories(self.feed_item, data)

        category_count = FeedItemCategory.objects.filter(
            item=self.feed_item
        ).count()
        self.assertEqual(category_count, 1)
        feed_item_category = FeedItemCategory.objects.filter(
            item=self.feed_item
        ).first()
        self.assertEqual(feed_item_category.keyword, new_keyword)

    # update tests
    def test__update__return_feed_item__on_valid_data(self) -> None:
        data = {
            'title': self.feed_item.title
        }

        feed_item = FeedItemUpdater.update(self.feed.id, data)

        self.assertEqual(self.feed_item.id, feed_item.id)


class FeedUpdaterTestCase(BaseTestCase):
    def setUp(self) -> None:
        """
        Set self.user before tests.
        """
        self.set_user()
        self.set_feed_subscription()
        self.set_feed()

    # _get_feed_subscription tests
    def test__get_feed_subscription__raise__if_not_exists(self) -> None:
        with self.assertRaises(FeedUpdaterDoesntExistError):
            FeedUpdater._get_feed_subscription(0)

    def test__get_feed_subscription__return__if_exists(self) -> None:
        feed_subscription = FeedUpdater._get_feed_subscription(
            self.feed_subscription.id
        )
        self.assertEqual(feed_subscription.id, self.feed_subscription.id)

    # _get_feed_data tests
    def test__get_feed_data__raise_exception__on_invalid_url(self) -> None:
        with self.assertRaises(FeedUpdaterInvalidRSSError):
            FeedUpdater._get_feed_data('invalid_url')

    @vcr.use_cassette(
        'feeds/tests/vcr_cassettes/'
        'test__get_feed_data__raise_exception__on_not_rss_url.yaml'
    )
    def test__get_feed_data__raise_exception__on_not_rss_url(self) -> None:
        with self.assertRaises(FeedUpdaterInvalidRSSError):
            FeedUpdater._get_feed_data('https://www.google.com/')

    @vcr.use_cassette(
        'feeds/tests/vcr_cassettes/'
        'test__get_feed_data__dont_raise_exception__on_valid_url.yaml'
    )
    def test__get_feed_data__dont_raise_exception__on_valid_url(self) -> None:
        try:
            FeedUpdater._get_feed_data('http://www.nu.nl/rss/Algemeen')
        except FeedUpdaterInvalidRSSError:
            self.fail('clean() raised ExceptionType unexpectedly.')

    # _update_categories tests
    def test__update_categories__replace_old_categories_with_new(self) -> None:
        FeedCategory.objects.create(
            feed=self.feed,
            keyword='old_keyword'
        )
        new_keyword = 'keyword'
        feed_data = FeedParserDict({
            'feed': {
                'tags': [{
                    'term': 'keyword',
                }]
            }
        })

        FeedUpdater._update_categories(self.feed, feed_data)

        category_count = FeedCategory.objects.filter(feed=self.feed).count()
        self.assertEqual(category_count, 1)
        feed_category = FeedCategory.objects.filter(feed=self.feed).first()
        self.assertEqual(feed_category.keyword, new_keyword)

    # _update_feed tests
    def test__update_feed__creates_feed__if_relation_is_missing(self) -> None:
        self.feed.delete()
        title = 'test2'
        data = FeedParserDict({
            'feed': {
                'title': title
            }
        })

        FeedUpdater._update_feed(self.feed_subscription, data)

        self.assertEqual(self.feed_subscription.feed.title, title)

    def test__update_feed__updates_feed__if_relation_exists(self) -> None:
        title = 'test2'
        data = FeedParserDict({
            'feed': {
                'title': title
            }
        })

        FeedUpdater._update_feed(self.feed_subscription, data)
        self.feed.refresh_from_db()

        self.assertEqual(self.feed.title, title)

    # update tests
    @vcr.use_cassette(
        'feeds/tests/vcr_cassettes/'
        'test__update__save_and_return_data__on_valid_rss.yaml'
    )
    def test__update__save_and_return_data__on_valid_rss(self) -> None:
        feed_subscription = FeedSubscription.objects.create(
            owner=self.user,
            url='http://www.nu.nl/rss/Algemeen'
        )

        feed, feed_data = FeedUpdater.update(feed_subscription.id)

        self.assertIsNotNone(feed.id)
        self.assertTrue(bool(feed_data))

    @vcr.use_cassette(
        'feeds/tests/vcr_cassettes/'
        'test__update__fail__on_invalid_rss.yaml'
    )
    def test__update__fail__on_invalid_rss(self) -> None:
        feed_subscription = FeedSubscription.objects.create(
            owner=self.user,
            url='https://www.google.com/'
        )

        with self.assertRaises(FeedUpdaterInvalidRSSError):
            FeedUpdater.update(feed_subscription.id)

        feed_subscription.refresh_from_db()
        self.assertEqual(feed_subscription.retries, 1)
