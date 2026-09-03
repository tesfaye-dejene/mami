from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, MyOrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="orders")
router.register("me/orders", MyOrderViewSet, basename="my-orders")
urlpatterns = router.urls
