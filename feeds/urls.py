from rest_framework import routers

from feeds.views import FeedSubscriptionViewSet, FeedViewSet

router = routers.SimpleRouter()
router.register(
    'subscriptions',
    FeedSubscriptionViewSet,
    basename='FeedSubscription'
)
router.register('', FeedViewSet, basename='Feed')
urlpatterns = router.urls
