from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, permissions, decorators, response, status
from apps.customers.infrastructure.models import Customer
from .serializers import CustomerSerializer
User = get_user_model()

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]
    def get_queryset(self):
        qs = Customer.objects.filter(deleted_at__isnull=True).select_related("user")
        search = self.request.query_params.get("search")
        if search: qs = qs.filter(full_name__icontains=search)
        return qs
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", "")) or "Customer123!"
        if not username or not data.get("full_name"):
            return response.Response({"detail":"username and full_name are required."}, status=400)
        if User.objects.filter(username=username).exists():
            return response.Response({"detail":"Username already exists."}, status=400)
        user = User.objects.create_user(username=username, email=data.get("email", ""), password=password)
        customer = Customer.objects.create(user=user, full_name=data["full_name"], phone=data.get("phone",""), email=data.get("email",""), address=data.get("address",""))
        return response.Response(self.get_serializer(customer).data, status=201)
    @decorators.action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        ids = request.data.get("customer_ids", [])
        count = Customer.objects.filter(id__in=ids, deleted_at__isnull=True).update(deleted_at=timezone.now(), is_active=False)
        return response.Response({"deleted": count})
    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now(); instance.is_active = False
        instance.save(update_fields=["deleted_at","is_active","updated_at"])

class MyProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def retrieve(self, request, pk=None):
        customer = Customer.objects.get(user=request.user)
        return response.Response(CustomerSerializer(customer).data)
    def update(self, request, pk=None, partial=False):
        customer = Customer.objects.get(user=request.user)
        serializer = CustomerSerializer(customer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True); serializer.save()
        return response.Response(serializer.data)
