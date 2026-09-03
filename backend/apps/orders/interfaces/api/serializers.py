from rest_framework import serializers
from apps.orders.infrastructure.models import Order, OrderItem
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem; fields=["id","product","product_name","quantity","unit_price","subtotal"]
class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True, read_only=True); customer_name=serializers.CharField(source="customer.full_name", read_only=True)
    class Meta:
        model=Order; fields=["id","customer","customer_name","status","payment_status","total_amount","items","created_at","updated_at"]
        read_only_fields=["id","customer","customer_name","total_amount","items","created_at","updated_at"]
class CreateOrderSerializer(serializers.Serializer):
    items=serializers.ListField(child=serializers.DictField(), allow_empty=False)
    def validate_items(self, items):
        for item in items:
            if "product_id" not in item or "quantity" not in item: raise serializers.ValidationError("Each item needs product_id and quantity.")
            try:
                if int(item["quantity"]) <= 0: raise ValueError
            except (TypeError, ValueError): raise serializers.ValidationError("Quantity must be a positive integer.")
        return items
