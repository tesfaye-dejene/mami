from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<uuid:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<uuid:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<uuid:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("orders/<uuid:order_id>/", views.order_detail, name="order_detail"),
    # Admin / owner only
    path("owner/", views.admin_dashboard, name="admin_dashboard"),
    path("owner/orders/", views.admin_orders, name="admin_orders"),
    path("owner/orders/<uuid:order_id>/status/", views.admin_order_status, name="admin_order_status"),
    path("owner/orders/<uuid:order_id>/payment/", views.admin_order_payment, name="admin_order_payment"),
    path("owner/products/", views.admin_products, name="admin_products"),
]
