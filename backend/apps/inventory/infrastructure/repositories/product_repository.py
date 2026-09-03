from apps.inventory.infrastructure.models import Product

class DjangoProductRepository:
    def create(self, data):
        return Product.objects.create(**data)

    def get(self, product_id):
        return Product.objects.get(id=product_id)

    def list(self):
        return Product.objects.filter(is_active=True)

    def change_price(self, product_id, new_price):
        product = self.get(product_id)
        product.price = new_price
        product.save(update_fields=["price", "updated_at"])
        return product
