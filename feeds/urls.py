from rest_framework import routers

from feeds.views import FeedItemViewSet, FeedSubscriptionViewSet, FeedViewSet

router = routers.SimpleRouter()
router.register(
    'subscriptions',
    FeedSubscriptionViewSet,
    basename='FeedSubscription'
)
router.register('items', FeedItemViewSet, basename='FeedItem')
router.register('', FeedViewSet, basename='Feed')
urlpatterns = router.urls
