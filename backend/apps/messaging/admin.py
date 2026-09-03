from django.contrib import admin
from .infrastructure.models import Message, MessageReply

class ReplyInline(admin.TabularInline):
    model = MessageReply
    extra = 1
    fields = ("message_text", "sender", "created_at")
    readonly_fields = ("sender", "created_at")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "customer", "is_closed", "created_at")
    search_fields = ("subject", "message", "customer__full_name", "customer__user__username")
    list_filter = ("is_closed", "created_at")
    list_per_page = 20
    inlines = [ReplyInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, MessageReply) and not instance.sender_id:
                instance.sender = request.user
            instance.save()
        formset.save_m2m()
