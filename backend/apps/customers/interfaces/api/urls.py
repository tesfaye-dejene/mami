from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CustomerViewSet, MyProfileViewSet
router = DefaultRouter(); router.register("customers", CustomerViewSet, basename="customers")
urlpatterns = router.urls + [path("me/profile/", MyProfileViewSet.as_view({"get":"retrieve","put":"update","patch":"partial_update"}))]
