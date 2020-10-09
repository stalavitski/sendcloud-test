from typing import Dict

from celery import shared_task
from celery.utils.log import get_task_logger

from feeds.models import FeedSubscription
from feeds.utils.feedupdater import FeedItemUpdater, FeedUpdater

logger = get_task_logger(__name__)


@shared_task
def update_feeds() -> None:
    """
    Update all active subscriptions that are not running.
    """
    queryset = (
        FeedSubscription
        .objects
        .filter(
            is_stopped=False,
            status=FeedSubscription.STATUS_READY
        )
        .values_list('id', flat=True)
    )

    for subscription_id in queryset.iterator():
        update_feed.delay(subscription_id)


@shared_task
def update_feed(feed_subscription_id: int) -> None:
    """
    Update Feed based on FeedSubscription.

    :param feed_subscription_id: FeedSubscription.id for related Feed.
    """
    try:
        feed, feed_items_data = FeedUpdater.update(feed_subscription_id)
    except Exception as e:
        logger.error(e)
        return

    for feed_item_data in feed_items_data:
        update_feed_item.delay(feed.id, feed_item_data)


@shared_task
def update_feed_item(feed_id: int, feed_item_data: Dict) -> None:
    """
    Update FeedItem based on Feed.

    :param feed_id: Feed.id for related FeedItem.
    :param feed_item_data: Dict with parsed FeedItem data.
    """
    try:
        FeedItemUpdater.update(feed_id, feed_item_data)
    except Exception as e:
        logger.error(e)
