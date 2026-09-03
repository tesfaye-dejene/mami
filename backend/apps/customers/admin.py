from django.contrib import admin
from django.utils import timezone
from .infrastructure.models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "username_display", "email", "phone", "is_active", "created_at")
    search_fields = ("full_name", "email", "phone", "user__username")
    list_filter = ("is_active", "created_at")
    list_per_page = 20
    actions = ("soft_delete_selected", "restore_selected")

    def get_queryset(self, request):
        return Customer.objects.select_related("user")

    @admin.display(description="Username", ordering="user__username")
    def username_display(self, obj):
        return obj.user.username

    @admin.action(description="Soft-delete selected customers")
    def soft_delete_selected(self, request, queryset):
        queryset.update(deleted_at=timezone.now(), is_active=False)

    @admin.action(description="Restore selected customers")
    def restore_selected(self, request, queryset):
        queryset.update(deleted_at=None, is_active=True)

    def delete_model(self, request, obj):
        obj.deleted_at = timezone.now()
        obj.is_active = False
        obj.save(update_fields=["deleted_at", "is_active", "updated_at"])

    def delete_queryset(self, request, queryset):
        queryset.update(deleted_at=timezone.now(), is_active=False)
