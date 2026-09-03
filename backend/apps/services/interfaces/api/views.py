from rest_framework import viewsets, permissions
from apps.services.infrastructure.models import Service
from .serializers import ServiceSerializer
class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    def get_queryset(self):
        qs = Service.objects.all().order_by("name")
        return qs if self.request.user.is_staff else qs.filter(is_active=True)
    def get_permissions(self):
        return [permissions.IsAdminUser()] if self.action in ["create","update","partial_update","destroy"] else [permissions.AllowAny()]
