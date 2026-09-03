from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.customers.infrastructure.models import Customer
from apps.inventory.infrastructure.models import Product
from apps.services.infrastructure.models import Service

class Command(BaseCommand):
    help = "Create/reset the local development admin and add sample catalog data."
    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin")
        parser.add_argument("--password", default="Admin12345!")
        parser.add_argument("--email", default="admin@example.com")
    def handle(self, *args, **opts):
        User = get_user_model()
        u, created = User.objects.get_or_create(username=opts["username"], defaults={"email": opts["email"]})
        u.email = opts["email"]; u.is_staff = True; u.is_superuser = True; u.is_active = True; u.set_password(opts["password"]); u.save()
        self.stdout.write(self.style.SUCCESS(f"Admin ready: {u.username}"))
        Customer.objects.get_or_create(user=u, defaults={"full_name":"Administrator", "email":u.email})
        Token.objects.get_or_create(user=u)
        if not Product.objects.exists():
            Product.objects.bulk_create([
                Product(name="Premium Rice", description="Quality rice for everyday cooking.", price="2500.00", stock_quantity=50),
                Product(name="Cooking Oil", description="Clean and reliable cooking oil.", price="950.00", stock_quantity=80),
                Product(name="Wheat Flour", description="Fine flour suitable for baking and cooking.", price="1200.00", stock_quantity=60),
            ])
        if not Service.objects.exists():
            Service.objects.bulk_create([
                Service(name="Home Delivery", description="Reliable delivery for orders placed through our website."),
                Service(name="Bulk Orders", description="Special handling and support for larger customer orders."),
                Service(name="Customer Support", description="Send us a message and our team can reply from the admin panel."),
            ])
        self.stdout.write(self.style.SUCCESS("Demo catalog is ready."))
