from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Django Templates shop frontend
    path("", include("apps.shop.urls")),
    # REST API (kept for optional React or other clients)
    path("api/v1/auth/", include("apps.customers.interfaces.api.auth_urls")),
    path("api/v1/", include("apps.inventory.interfaces.api.urls")),
    path("api/v1/", include("apps.customers.interfaces.api.urls")),
    path("api/v1/", include("apps.orders.interfaces.api.urls")),
    path("api/v1/", include("apps.messaging.interfaces.api.urls")),
    path("api/v1/", include("apps.services.interfaces.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
