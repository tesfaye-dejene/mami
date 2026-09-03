from rest_framework import viewsets, permissions, status, response, decorators
from apps.customers.infrastructure.models import Customer
from apps.orders.application.use_cases.create_order import CreateOrder
from apps.orders.infrastructure.models import Order
from .serializers import OrderSerializer, CreateOrderSerializer
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    def get_queryset(self):
        qs = Order.objects.select_related("customer").prefetch_related("items__product")
        return qs if self.request.user.is_staff else qs.filter(customer__user=self.request.user)
    def get_permissions(self):
        if self.action == "create": return [permissions.IsAuthenticated()]
        if self.action in ["list","retrieve"]: return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        try: customer = Customer.objects.get(user=request.user, is_active=True, deleted_at__isnull=True)
        except Customer.DoesNotExist: return response.Response({"detail":"Customer profile not found."}, status=400)
        try: order = CreateOrder().execute(customer, serializer.validated_data["items"])
        except Exception as exc: return response.Response({"detail":str(exc)}, status=400)
        return response.Response(OrderSerializer(order, context={"request":request}).data, status=201)
    @decorators.action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        order = self.get_object(); value = request.data.get("status")
        if value not in {x[0] for x in Order.Status.choices}: return response.Response({"detail":"Invalid order status."}, status=400)
        order.status=value; order.save(update_fields=["status","updated_at"]); return response.Response(OrderSerializer(order).data)
    @decorators.action(detail=True, methods=["patch"])
    def update_payment(self, request, pk=None):
        order=self.get_object(); value=request.data.get("payment_status")
        if value not in {x[0] for x in Order.PaymentStatus.choices}: return response.Response({"detail":"Invalid payment status."}, status=400)
        order.payment_status=value; order.save(update_fields=["payment_status","updated_at"]); return response.Response(OrderSerializer(order).data)
class MyOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return Order.objects.filter(customer__user=self.request.user).select_related("customer").prefetch_related("items__product")
