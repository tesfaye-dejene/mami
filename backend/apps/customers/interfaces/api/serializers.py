from rest_framework import serializers
from apps.customers.infrastructure.models import Customer
class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Customer
        fields = ["id","user","username","full_name","phone","email","address","is_active","deleted_at","created_at","updated_at"]
        read_only_fields = ["id","user","username","created_at","updated_at","deleted_at"]
