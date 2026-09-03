from django.db import migrations, models
import uuid
class Migration(migrations.Migration):
    initial=True
    dependencies=[]
    operations=[
        migrations.CreateModel(name='Product',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('name',models.CharField(max_length=200)),('description',models.TextField(blank=True)),('price',models.DecimalField(decimal_places=2,max_digits=12)),('stock_quantity',models.PositiveIntegerField(default=0)),('is_available',models.BooleanField(default=True)),('is_active',models.BooleanField(default=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True))],options={'ordering':['-created_at']}),
        migrations.CreateModel(name='ProductImage',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('image',models.ImageField(upload_to='products/')),('is_primary',models.BooleanField(default=False)),('created_at',models.DateTimeField(auto_now_add=True)),('product',models.ForeignKey(on_delete=models.deletion.CASCADE,related_name='images',to='inventory.product'))]),
    ]
