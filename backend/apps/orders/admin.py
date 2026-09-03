from django.contrib import admin
from .infrastructure.models import Order, OrderItem
class OrderItemInline(admin.TabularInline):
    model=OrderItem; extra=0; readonly_fields=("product_name","quantity","unit_price","subtotal")
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=("id","customer","total_amount","status","payment_status","created_at")
    search_fields=("customer__full_name","customer__user__username")
    list_filter=("status","payment_status","created_at")
    readonly_fields=("total_amount","created_at","updated_at")
    inlines=[OrderItemInline]
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=("order","product_name","quantity","unit_price","subtotal")
