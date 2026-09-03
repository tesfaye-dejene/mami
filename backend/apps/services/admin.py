from django.contrib import admin
from .infrastructure.models import Service
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display=("name","is_active","updated_at")
    search_fields=("name","description")
    list_filter=("is_active",)
