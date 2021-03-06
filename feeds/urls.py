from django.urls import path
from rest_framework import routers

from feeds.views import (
    FeedItemViewSet,
    FeedSubscriptionForceUpdateView,
    FeedSubscriptionRetryView,
    FeedSubscriptionViewSet,
    FeedViewSet
)

router = routers.SimpleRouter()
router.register(
    'subscriptions',
    FeedSubscriptionViewSet,
    basename='FeedSubscription'
)
router.register('items', FeedItemViewSet, basename='FeedItem')
router.register('', FeedViewSet, basename='Feed')
urlpatterns = [
    path('subscriptions/<pk>/retry', FeedSubscriptionRetryView.as_view()),
    path(
        'subscriptions/<pk>/force_update',
        FeedSubscriptionForceUpdateView.as_view()
    ),
]
urlpatterns += router.urls
