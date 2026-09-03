from rest_framework import serializers
from apps.inventory.infrastructure.models import Product, ProductImage
class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = ProductImage; fields = ["id","image","image_url","is_primary"]
    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request and obj.image else (obj.image.url if obj.image else None)
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    class Meta:
        model = Product; fields = ["id","name","description","price","stock_quantity","is_available","is_active","images","primary_image","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]
    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first() or obj.images.first()
        if not image or not image.image: return None
        request = self.context.get("request")
        return request.build_absolute_uri(image.image.url) if request else image.image.url
    def validate_price(self, value):
        if value < 0: raise serializers.ValidationError("Price cannot be negative.")
        return value
