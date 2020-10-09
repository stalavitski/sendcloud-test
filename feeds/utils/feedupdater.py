from datetime import datetime
from time import mktime
from typing import Tuple, Union

import feedparser
from django.db import transaction
from django.utils.translation import gettext as _
from feedparser.util import FeedParserDict

from feeds.models import (
    Feed,
    FeedCategory,
    FeedItem,
    FeedItemCategory,
    FeedSubscription
)


class FeedUpdaterDoesntExistError(Exception):
    pass


class FeedUpdaterInvalidRSSError(Exception):
    pass


class BaseFeedUpdater:
    @classmethod
    def get_pub_date(
            cls,
            data: Union[FeedParserDict, dict]
    ) -> Union[datetime, None]:
        """
        Get publication date as datetime if set.

        :param data: Parsed RSS feed data.
        :return: Publication date datetime or None.
        """
        structured_pub_date = tuple(data.get('published_parsed', []))

        if structured_pub_date:
            time = mktime(structured_pub_date)
            return datetime.fromtimestamp(time)

        return


class FeedItemUpdater(BaseFeedUpdater):
    @classmethod
    def _get_feed(cls, feed_id: int) -> Feed:
        """
        Get Feed instance.

        :param feed_id: Feed id.
        :return: Feed instance.
        """
        try:
            feed = (
                Feed
                .objects
                .get(id=feed_id)
            )
        except Feed.DoesNotExist:
            raise FeedUpdaterDoesntExistError(
                _('Feed with id={} does not exist.').format(feed_id)
            )

        return feed

    @classmethod
    def _update_feed_item(cls, feed: Feed, feed_item_data: dict) -> FeedItem:
        """
        Create or update FeedItem based on RSS feed item data.

        :param feed: Feed instance related to FeedItem.
        :param feed_item_data: RSS feed item data.
        :return: Updated FeedItem instance.
        """
        enclosure = next(iter(feed_item_data.get('enclosures', [])), {})
        # Create a filed_name:value dict out of fetched data for FeedItem
        data = {
            'author': feed_item_data.get('author'),
            'comments': feed_item_data.get('comments'),
            'description': feed_item_data.get('summary'),
            'enclosure_length': enclosure.get('length'),
            'enclosure_type': enclosure.get('type'),
            'enclosure_url': enclosure.get('href'),
            'feed': feed,
            'guid': feed_item_data.get('id'),
            'link': feed_item_data.get('link'),
            'pub_date': cls.get_pub_date(feed_item_data),
            'title': feed_item_data.get('title')
        }
        feed_item, created = FeedItem.objects.get_or_create(
            defaults=data,
            feed=feed,
            title=data['title']
        )

        if not created:
            # Update FeedItem with fetched values
            for name, value in data.items():
                setattr(feed_item, name, value)

        feed_item.save()
        return feed_item

    @classmethod
    def _update_categories(
            cls,
            feed_item: FeedItem,
            feed_item_data: dict
    ) -> None:
        """
        Sets FeedItemCategory objects to FeedItem.

        :param feed_item: FeedItem instance to assign categories.
        :param feed_item_data: Dict that may include categories.
        """
        feed_item.categories.all().delete()
        categories = feed_item_data.get('tags', [])

        for category in categories:
            FeedItemCategory.objects.create(
                domain=category.get('scheme'),
                item=feed_item,
                keyword=category.get('term'),
                label=category.get('label')
            )

    @classmethod
    @transaction.atomic
    def update(cls, feed_id: int, feed_item_data: dict) -> FeedItem:
        """
        Create/update FeedItem and related instances of FeedItemCategory.

        :param feed_id: Feed id to update related FeedItem.
        :param feed_item_data: Dict of parsed RSS feed item data.
        :return: FeedItem instance.
        """
        feed = cls._get_feed(feed_id)
        feed_item = cls._update_feed_item(feed, feed_item_data)
        cls._update_categories(feed_item, feed_item_data)
        return feed_item


class FeedUpdater(BaseFeedUpdater):
    @classmethod
    def _get_feed_subscription(
            cls,
            feed_subscription_id: int
    ) -> FeedSubscription:
        """
        Get FeedSubscription instance.

        :param feed_subscription_id: FeedSubscription id.
        :return: FeedSubscription instance
        """
        try:
            feed_subscription = (
                FeedSubscription
                .objects
                .prefetch_related('feed', 'feed__categories')
                .get(id=feed_subscription_id)
            )
        except FeedSubscription.DoesNotExist:
            raise FeedUpdaterDoesntExistError(
                _('FeedSubscription with id={} does not exist.')
                .format(feed_subscription_id)
            )

        return feed_subscription

    @classmethod
    def _get_feed_data(cls, url: str) -> FeedParserDict:
        """
        Get parsed data from RSS url.

        :param url: Url to RSS page.
        :return: Parsed RSS data.
        """
        feed_data = feedparser.parse(url)

        if feed_data.get('bozo'):
            raise FeedUpdaterInvalidRSSError(
                _('Failed to load a valid RSS from {}.').format(url)
            )

        return feed_data

    @classmethod
    def _update_categories(cls, feed: Feed, feed_data: FeedParserDict) -> None:
        """
        Sets FeedCategory objects to Feed.

        :param feed: Feed instance to assign categories.
        :param feed_data: FeedParserDict that may include categories.
        """
        feed.categories.all().delete()
        categories = feed_data.feed.get('tags', [])

        for category in categories:
            FeedCategory.objects.create(
                domain=category.get('scheme'),
                feed=feed,
                keyword=category.get('term'),
                label=category.get('label')
            )

    @classmethod
    def _update_feed(
            cls,
            feed_subscription: FeedSubscription,
            feed_data: FeedParserDict,

    ) -> Feed:
        """
        Create or update Feed based on parsed data.

        :param feed_subscription: FeedSubscription related instance.
        :param feed_data: Parsed RSS data.
        :return: Processed Feed instance.
        """
        cloud = feed_data.feed.get('cloud', {})
        image = feed_data.feed.get('image', {})
        text_input = feed_data.feed.get('textinput', {})
        # Create a filed_name:value dict out of fetched data for Feed
        data = {
            'cloud_domain': cloud.get('domain'),
            'cloud_path': cloud.get('path'),
            'cloud_port': cloud.get('port'),
            'cloud_protocol': cloud.get('protocol'),
            'cloud_register_procedure': cloud.get('registerProcedure'),
            'copyright': feed_data.feed.get('rights'),
            'description': feed_data.feed.get('subtitle'),
            'docs': feed_data.feed.get('docs'),
            'encoding': feed_data.get('encoding'),
            'generator': feed_data.feed.get('generator'),
            'image_description': image.get('description'),
            'image_height': image.get('height'),
            'image_link': image.get('width'),
            'image_title': image.get('title'),
            'image_url': image.get('href'),
            'image_width': image.get('width'),
            'language': feed_data.feed.get('language'),
            'link': feed_data.feed.get('link'),
            'managing_editor': feed_data.feed.get('author'),
            'pub_date': cls.get_pub_date(feed_data.feed),
            'subscription': feed_subscription,
            'text_input_description': text_input.get('description'),
            'text_input_link': text_input.get('link'),
            'text_input_name': text_input.get('name'),
            'text_input_title': text_input.get('title'),
            'title': feed_data.feed.get('title'),
            'ttl': feed_data.feed.get('ttl'),
            'version': feed_data.get('version'),
            'web_master': feed_data.feed.get('publisher')
        }

        try:
            feed = feed_subscription.feed

            # Update Feed with fetched values
            for name, value in data.items():
                setattr(feed, name, value)
        except FeedSubscription.feed.RelatedObjectDoesNotExist:
            # Make a new Feed instance with fetched values
            feed = Feed(**data)

        feed.save()
        return feed

    @classmethod
    def update(cls, feed_subscription_id: int) -> Tuple[Feed, FeedParserDict]:
        """
        Parse feed from RSS page, create/update Feed and related instances of
        FeedCategory.

        :param feed_subscription_id: FeedSubscription id to update RSS.
        :return: Tuple with Feed instance and parsed RSS data.
        """
        feed_subscription = cls._get_feed_subscription(feed_subscription_id)
        feed_subscription.in_progress()

        try:
            with transaction.atomic():
                feed_data = cls._get_feed_data(feed_subscription.url)
                feed = cls._update_feed(feed_subscription, feed_data)
                cls._update_categories(feed, feed_data)
                feed_subscription.success()
        except Exception as e:
            feed_subscription.failure()
            raise e

        return feed, feed_data.get('entries', FeedParserDict())
