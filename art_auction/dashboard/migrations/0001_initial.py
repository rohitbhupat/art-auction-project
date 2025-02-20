# Generated by Django 4.1.4 on 2022-12-14 09:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OrderModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateField(auto_now_add=True)),
                ('order_qty', models.IntegerField(default=0)),
                ('order_price', models.FloatField(default=0.0)),
                ('delivery_at', models.TextField(default=' ')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(default='', max_length=255)),
                ('product_price', models.IntegerField(default=0)),
                ('product_qty', models.IntegerField(default=1)),
                ('product_image', models.ImageField(upload_to='arts/')),
                ('product_cat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_mode', models.CharField(choices=[('1', 'UPI'), ('2', 'CARD'), ('3', 'TRANSFER'), ('4', 'OTHER')], max_length=255)),
                ('date', models.DateField(auto_now_add=True)),
                ('success_status', models.BooleanField(default=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.ordermodel')),
            ],
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.product'),
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
