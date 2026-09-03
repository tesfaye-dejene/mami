from django.contrib import admin
from .infrastructure.models import Product, ProductImage
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=("name","price","stock_quantity","is_available","is_active","updated_at")
    search_fields=("name","description")
    list_filter=("is_available","is_active")
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display=("product","is_primary","created_at")
    list_filter=("is_primary",)
