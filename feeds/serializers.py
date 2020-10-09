from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from feeds.models import (
    Feed,
    FeedCategory,
    FeedItem,
    FeedItemCategory,
    FeedSubscription
)
from feeds.tasks import update_feed


class FeedSubscriptionSerializer(serializers.ModelSerializer):
    feed = serializers.IntegerField(read_only=True, source='feed.id')
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ['feed', 'id', 'owner', 'url']
        model = FeedSubscription
        validators = [
            UniqueTogetherValidator(
                queryset=FeedSubscription.objects.all(),
                fields=['owner', 'url']
            )
        ]

    def create(self, validated_data: dict) -> FeedSubscription:
        """
        Create FeedSubscription and schedule async feed update.

        :param validated_data: Dict of serializer validated data.
        :return: Created instance of FeedSubscription.
        """
        instance = super().create(validated_data)
        update_feed.delay(instance.id)
        return instance


class FeedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = FeedCategory


class FeedSerializer(serializers.ModelSerializer):
    categories = FeedCategorySerializer(many=True, read_only=True)

    class Meta:
        exclude = []
        model = Feed


class FeedItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id', 'item']
        model = FeedItemCategory


class FeedItemSerializer(serializers.ModelSerializer):
    categories = FeedItemCategorySerializer(many=True, read_only=True)

    class Meta:
        exclude = []
        model = FeedItem
