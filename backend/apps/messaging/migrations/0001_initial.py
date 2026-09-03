from django.db import migrations, models
import django.db.models.deletion
import uuid
class Migration(migrations.Migration):
    initial=True
    dependencies=[('auth','0012_alter_user_first_name_max_length'),('customers','0001_initial')]
    operations=[
      migrations.CreateModel(name='Message',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('subject',models.CharField(max_length=200)),('message',models.TextField()),('is_closed',models.BooleanField(default=False)),('created_at',models.DateTimeField(auto_now_add=True)),('customer',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='messages',to='customers.customer'))]),
      migrations.CreateModel(name='MessageReply',fields=[('id',models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True,serialize=False)),('message_text',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),('message',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='replies',to='messaging.message')),('sender',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to='auth.user'))])
    ]
