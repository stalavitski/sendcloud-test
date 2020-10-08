from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

User = get_user_model()


class FeedSubscription(models.Model):
    owner = models.ForeignKey(User, models.CASCADE, 'feed_subscriptions')
    url = models.URLField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'url'],
                name='feeds_feedsubscription_owner_url_key'
            ),
        ]

    def clean(self) -> None:
        """
        Don't allow to save FeedSubscription with not unique owner+url.
        """
        not_unique = (
            FeedSubscription
            .objects
            .filter(owner=self.owner, url=self.url)
            .exclude(id=self.id)
            .exists()
        )

        if not_unique:
            raise ValidationError(
                _('Subscription to this feed is already exists.'),
                code='duplicated_subscription'
            )


class Feed(models.Model):
    cloud_domain = models.TextField(blank=True, null=True)
    cloud_path = models.TextField(blank=True, null=True)
    cloud_port = models.TextField(blank=True, null=True)
    cloud_protocol = models.TextField(blank=True, null=True)
    cloud_register_procedure = models.TextField(blank=True, null=True)
    copyright = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    docs = models.TextField(blank=True, null=True)
    encoding = models.TextField(blank=True, null=True)
    generator = models.TextField(blank=True, null=True)
    image_description = models.TextField(blank=True, null=True)
    image_height = models.TextField(blank=True, null=True)
    image_link = models.TextField(blank=True, null=True)
    image_title = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    image_width = models.TextField(blank=True, null=True)
    language = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    managing_editor = models.TextField(blank=True, null=True)
    # @TODO default to None
    pub_date = models.DateTimeField(blank=True, default=date.today, null=True)
    subscription = models.OneToOneField(
        FeedSubscription,
        models.CASCADE,
        related_name='feed'
    )
    text_input_description = models.TextField(blank=True, null=True)
    text_input_link = models.TextField(blank=True, null=True)
    text_input_name = models.TextField(blank=True, null=True)
    text_input_title = models.TextField(blank=True, null=True)
    title = models.TextField()
    ttl = models.TextField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)
    web_master = models.TextField(blank=True, null=True)


class FeedCategoryAbstract(models.Model):
    domain = models.TextField(blank=True, null=True)
    keyword = models.TextField()
    label = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class FeedCategory(FeedCategoryAbstract):
    feed = models.ForeignKey(Feed, models.CASCADE, 'categories')


class FeedItem(models.Model):
    author = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    enclosure_length = models.TextField(blank=True, null=True)
    enclosure_type = models.TextField(blank=True, null=True)
    enclosure_url = models.TextField(blank=True, null=True)
    feed = models.ForeignKey(Feed, models.CASCADE, 'items')
    guid = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField(blank=True, default=date.today, null=True)
    title = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['feed', 'link'],
                name='feeds_feeditem_feed_link_key'
            ),
        ]

    def clean(self) -> None:
        """
        Don't allow to save FeedItem with not unique feed+title.
        """
        not_unique = (
            FeedItem
            .objects
            .filter(feed=self.feed, title=self.title)
            .exclude(id=self.id)
            .exists()
        )

        if not_unique:
            raise ValidationError(
                _('Feed item with this title is already exists.'),
                code='duplicated_feed_item'
            )


class FeedItemCategory(FeedCategoryAbstract):
    item = models.ForeignKey(FeedItem, models.CASCADE, 'categories')
