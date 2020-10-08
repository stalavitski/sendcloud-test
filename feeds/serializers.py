from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from feeds.models import Feed, FeedSubscription
from feeds.utils.feedupdater import FeedUpdater


class FeedSubscriptionSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ['id', 'owner', 'url']
        model = FeedSubscription
        validators = [
            UniqueTogetherValidator(
                queryset=FeedSubscription.objects.all(),
                fields=['owner', 'url']
            )
        ]

    def create(self, validated_data):
        instance = super().create(validated_data)
        feed_updater = FeedUpdater(instance)
        feed_updater.update_feed()
        return instance


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = []
        model = Feed
