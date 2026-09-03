from rest_framework import viewsets, permissions
from apps.inventory.infrastructure.models import Product
from .serializers import ProductSerializer
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    def get_queryset(self):
        qs = Product.objects.prefetch_related("images").order_by("-created_at")
        if not self.request.user.is_staff: qs = qs.filter(is_active=True)
        return qs
    def get_permissions(self):
        return [permissions.IsAdminUser()] if self.action in ["create","update","partial_update","destroy"] else [permissions.AllowAny()]
