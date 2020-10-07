from rest_framework import routers

from feeds.views import FeedSubscriptionViewSet

router = routers.SimpleRouter()
router.register(
    'subscriptions',
    FeedSubscriptionViewSet,
    basename='FeedSubscription'
)
urlpatterns = router.urls
