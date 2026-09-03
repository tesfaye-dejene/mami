from rest_framework import generics, permissions, response, status
from apps.customers.infrastructure.models import Customer
from apps.messaging.infrastructure.models import Message, MessageReply
from .serializers import MessageSerializer, MessageReplySerializer
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class=MessageSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self):
        qs=Message.objects.select_related("customer").prefetch_related("replies__sender")
        return qs if self.request.user.is_staff else qs.filter(customer__user=self.request.user)
    def perform_create(self, serializer):
        if self.request.user.is_staff: return serializer.save()
        customer=Customer.objects.get(user=self.request.user, is_active=True, deleted_at__isnull=True)
        serializer.save(customer=customer)
class MessageReplyCreateView(generics.CreateAPIView):
    serializer_class=MessageReplySerializer; permission_classes=[permissions.IsAuthenticated]
    def perform_create(self, serializer):
        message=Message.objects.get(pk=self.kwargs["pk"])
        if not self.request.user.is_staff and message.customer.user_id != self.request.user.id: raise permissions.PermissionDenied()
        serializer.save(message=message, sender=self.request.user)
