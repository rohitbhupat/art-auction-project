# Generated by Django 5.0.6 on 2024-07-03 14:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0047_rename_is_read_notification_read_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.artwork'),
        ),
        migrations.AddField(
            model_name='notification',
            name='read_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
