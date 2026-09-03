from decimal import Decimal
from django.db import transaction
from apps.inventory.infrastructure.models import Product
from apps.orders.infrastructure.models import Order, OrderItem

class CreateOrder:
    @transaction.atomic
    def execute(self, customer, items):
        if not items:
            raise ValueError("An order must contain at least one item.")

        order = Order.objects.create(customer=customer)
        total = Decimal("0.00")

        for item in items:
            product = Product.objects.select_for_update().get(
                id=item["product_id"], is_active=True
            )
            quantity = int(item["quantity"])

            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")
            if not product.is_available or product.stock_quantity < quantity:
                raise ValueError(f"Product '{product.name}' is unavailable or out of stock.")

            unit_price = product.price
            subtotal = unit_price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )
            total += subtotal

        order.total_amount = total
        order.save(update_fields=["total_amount", "updated_at"])
        return order
