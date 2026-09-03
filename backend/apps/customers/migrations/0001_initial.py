from django.db import migrations, models
import django.db.models.deletion
import uuid
class Migration(migrations.Migration):
    initial=True
    dependencies=[('auth','0012_alter_user_first_name_max_length')]
    operations=[migrations.CreateModel(name='Customer',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('full_name',models.CharField(max_length=200)),('phone',models.CharField(blank=True,max_length=50)),('email',models.EmailField(blank=True,max_length=254)),('address',models.TextField(blank=True)),('is_active',models.BooleanField(default=True)),('deleted_at',models.DateTimeField(blank=True,null=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='customer',to='auth.user'))],options={'ordering':['-created_at']})]
