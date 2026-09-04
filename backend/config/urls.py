from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.static import serve
import os

from apps.shop import views as shop_views


urlpatterns = [
    # =========================================================
    # DJANGO ADMIN
    # =========================================================
    path("admin/", admin.site.urls),

    # =========================================================
    # REACT FRONTEND
    # Main customer-facing frontend
    # =========================================================
    path(
        "",
        TemplateView.as_view(template_name="frontend/index.html"),
        name="react_home",
    ),

    path(
        "react/",
        TemplateView.as_view(template_name="frontend/index.html"),
        name="react_frontend",
    ),

    # =========================================================
    # DJANGO TEMPLATE FRONTEND
    # Kept separately so BOTH React and Django templates work.
    # =========================================================
    path("shop/", include("apps.shop.urls")),

    # =========================================================
    # OWNER / ADMIN TEMPLATE DASHBOARD
    # =========================================================
    path(
        "owner/",
        shop_views.admin_dashboard,
        name="admin_dashboard",
    ),
    path(
        "owner/orders/",
        shop_views.admin_orders,
        name="admin_orders",
    ),
    path(
        "owner/orders/<uuid:order_id>/status/",
        shop_views.admin_order_status,
        name="admin_order_status",
    ),
    path(
        "owner/orders/<uuid:order_id>/payment/",
        shop_views.admin_order_payment,
        name="admin_order_payment",
    ),
    path(
        "owner/products/",
        shop_views.admin_products,
        name="admin_products",
    ),

    # =========================================================
    # REST API
    # =========================================================
    path(
        "api/v1/auth/",
        include("apps.customers.interfaces.api.auth_urls"),
    ),

    path(
        "api/v1/",
        include("apps.inventory.interfaces.api.urls"),
    ),

    path(
        "api/v1/",
        include("apps.customers.interfaces.api.urls"),
    ),

    path(
        "api/v1/",
        include("apps.orders.interfaces.api.urls"),
    ),

    path(
        "api/v1/",
        include("apps.messaging.interfaces.api.urls"),
    ),

    path(
        "api/v1/",
        include("apps.services.interfaces.api.urls"),
    ),
]


# =============================================================
# MEDIA FILES
# Always serve (needed on Render where DEBUG=0)
# =============================================================

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)


# =============================================================
# REACT STATIC ASSETS
# /assets/... -> React Vite build
# =============================================================

urlpatterns += [
    path(
        "assets/<path:path>",
        serve,
        {
            "document_root": os.path.join(
                settings.BASE_DIR,
                "static",
                "frontend",
                "assets",
            )
        },
    ),
]