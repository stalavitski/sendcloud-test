import logging
from urllib.error import URLError

import feedparser
from django.core.exceptions import ValidationError
from django.db import transaction

from feeds.models import Feed, FeedCategory, FeedItem, FeedItemCategory
from feeds.utils.tools import get_date_from_struct_time


class FeedItemUpdater:
    @transaction.atomic
    def update_item(self, feed, entry):
        pub_date = get_date_from_struct_time(
            entry.get('published_parsed')
        )
        enclosure = next(iter(entry.get('enclosures', [])), {})
        feed_item = FeedItem(
            author=entry.get('author'),
            comments=entry.get('comments'),
            description=entry.get('summary'),
            enclosure_length=enclosure.get('length'),
            enclosure_type=enclosure.get('type'),
            enclosure_url=enclosure.get('href'),
            feed=feed,
            guid=entry.get('id'),
            link=entry.get('link'),
            pub_date=pub_date,
            title=entry.get('title'),
        )

        try:
            feed_item.full_clean()
            feed_item.save()
        except ValidationError as e:
            logging.error(
                'Error occurred during FeedItem validation. Details:'
            )
            logging.error(entry)
            logging.error(e)
        else:
            categories = entry.get('tags', [])

            for category in categories:
                self._update_category(feed_item, category)

    def _update_category(self, feed_item, category):
        feed_item_category = FeedItemCategory(
            domain=category.get('scheme'),
            item=feed_item,
            keyword=category.get('term'),
            label=category.get('label'),
        )

        try:
            feed_item_category.full_clean()
            feed_item_category.save()
        except ValidationError as e:
            logging.error(
                'Error occurred during FeedItemCategory validation. Details:'
            )
            logging.error(category)
            logging.error(e)


class FeedUpdater:
    def __init__(self, feed_subscription):
        self.feed_subscription = feed_subscription

    def _save_feed_data(self, feed_data):
        try:
            cloud = feed_data.feed.get('cloud', {})
            image = feed_data.feed.get('image', {})
            text_input = feed_data.feed.get('textinput', {})
            feed = Feed(
                cloud_domain=cloud.get('domain'),
                cloud_path=cloud.get('path'),
                cloud_port=cloud.get('port'),
                cloud_protocol=cloud.get('protocol'),
                cloud_register_procedure=cloud.get('registerProcedure'),
                copyright=feed_data.feed.get('rights'),
                description=feed_data.feed.get('subtitle'),
                docs=feed_data.feed.get('docs'),
                encoding=feed_data.get('encoding'),
                generator=feed_data.feed.get('generator'),
                image_description=image.get('description'),
                image_height=image.get('height'),
                image_link=image.get('width'),
                image_title=image.get('title'),
                image_url=image.get('href'),
                image_width=image.get('width'),
                language=feed_data.feed.get('language'),
                link=feed_data.feed.get('link'),
                managing_editor=feed_data.feed.get('author'),
                pub_date=get_date_from_struct_time(
                    feed_data.feed.get('published_parsed')
                ),
                subscription=self.feed_subscription,
                text_input_description=text_input.get('description'),
                text_input_link=text_input.get('link'),
                text_input_name=text_input.get('name'),
                text_input_title=text_input.get('title'),
                title=feed_data.feed.get('title'),
                ttl=feed_data.feed.get('ttl'),
                version=feed_data.get('version'),
                web_master=feed_data.feed.get('publisher'),
            )
            feed.full_clean()
            feed.save()

            categories = feed_data.feed.get('tags', [])

            for category in categories:
                self._update_category(feed, category)

            for entry in feed_data.get('entries', []):
                feed_updater = FeedItemUpdater()
                feed_updater.update_item(feed, entry)
        except ValidationError as e:
            logging.error(e)

    def _update_category(self, feed, category):
        feed_category = FeedCategory(
            domain=category.get('scheme'),
            feed=feed,
            keyword=category.get('term'),
            label=category.get('label'),
        )

        try:
            feed_category.full_clean()
            feed_category.save()
        except ValidationError as e:
            logging.error(
                'Error occurred during FeedCategory validation. Details:'
            )
            logging.error(category)
            logging.error(e)

    @transaction.atomic
    def update_feed(self):
        try:
            feed_data = feedparser.parse(self.feed_subscription.url)
        except URLError as e:
            logging.error(
                'Failed to load feed from {}. Details:'.format(
                    self.feed_subscription.url
                )
            )
            logging.error(e)
        else:
            if feed_data.status < 400:
                self._save_feed_data(feed_data)
            else:
                logging.error(
                    'Failed to load feed from {}. Status: {}.'.format(
                        self.feed_subscription.url,
                        feed_data.status
                    )
                )
