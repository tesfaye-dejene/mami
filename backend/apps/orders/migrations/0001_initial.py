from django.db import migrations, models
import django.db.models.deletion
import uuid
class Migration(migrations.Migration):
    initial=True
    dependencies=[('customers','0001_initial'),('inventory','0001_initial')]
    operations=[
      migrations.CreateModel(name='Order',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('status',models.CharField(choices=[('PENDING','Pending'),('CONFIRMED','Confirmed'),('PROCESSING','Processing'),('COMPLETED','Completed'),('CANCELLED','Cancelled')],default='PENDING',max_length=20)),('payment_status',models.CharField(choices=[('PENDING','Pending'),('PAID','Paid'),('FAILED','Failed'),('REFUNDED','Refunded')],default='PENDING',max_length=20)),('total_amount',models.DecimalField(decimal_places=2,default=0,max_digits=12)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('customer',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='orders',to='customers.customer'))],options={'ordering':['-created_at']}),
      migrations.CreateModel(name='OrderItem',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('product_name',models.CharField(max_length=200)),('quantity',models.PositiveIntegerField()),('unit_price',models.DecimalField(decimal_places=2,max_digits=12)),('subtotal',models.DecimalField(decimal_places=2,max_digits=12)),('order',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='items',to='orders.order')),('product',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to='inventory.product'))],options={'ordering':['id']})
    ]
