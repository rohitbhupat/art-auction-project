# Generated by Django 5.0.6 on 2024-05-31 04:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_delete_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 5, 31, 4, 56, 27, 401033, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]