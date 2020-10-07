from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from feeds.models import FeedSubscription


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
