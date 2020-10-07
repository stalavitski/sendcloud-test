from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class FeedSubscription(models.Model):
    owner = models.ForeignKey(User, models.CASCADE, 'feed_subscriptions')
    url = models.URLField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'url'],
                name='feeds_feed_owner_url_key')
        ]
