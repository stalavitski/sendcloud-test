from django.urls import path
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken import views
from rest_framework.authtoken.serializers import AuthTokenSerializer

from users.views import CreateUserView

# Set AuthTokenSerializer to provide a correct schema generation for drf_yasg
obtain_auth_token_view = swagger_auto_schema(
    method='post',
    request_body=AuthTokenSerializer
)(views.obtain_auth_token)


urlpatterns = [
    path('auth/', obtain_auth_token_view),
    path('register/', CreateUserView.as_view()),
]
