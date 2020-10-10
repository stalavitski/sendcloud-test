from django.conf import settings
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title=settings.OPENAPI_TITLE,
        default_version=settings.OPENAPI_VERSION,
        description=settings.OPENAPI_DESCRIPTION,
        terms_of_service=settings.OPENAPI_TERMS,
        contact=openapi.Contact(email=settings.OPENAPI_CONTACT),
        license=openapi.License(name=settings.OPENAPI_LICENSE),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/feeds/', include('feeds.urls')),
    path('api/users/', include('users.urls')),
    # Swagger
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
]
