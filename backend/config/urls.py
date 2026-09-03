from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.static import serve
import os

urlpatterns = [
    path("admin/", admin.site.urls),

    # REST API
    path("api/v1/auth/", include("apps.customers.interfaces.api.auth_urls")),
    path("api/v1/", include("apps.inventory.interfaces.api.urls")),
    path("api/v1/", include("apps.customers.interfaces.api.urls")),
    path("api/v1/", include("apps.orders.interfaces.api.urls")),
    path("api/v1/", include("apps.messaging.interfaces.api.urls")),
    path("api/v1/", include("apps.services.interfaces.api.urls")),

    # React frontend (everything else)
    path("", TemplateView.as_view(template_name="frontend/index.html")),
]

# Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve React assets in production
if not settings.DEBUG:
    urlpatterns += [
        path(
            "assets/<path:path>",
            serve,
            {"document_root": os.path.join(settings.BASE_DIR, "static", "frontend", "assets")},
        ),
    ]