# Generated by Django 5.1.6 on 2025-02-19 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0101_alter_artwork_enable_ar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='enable_ar',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]
