# Generated by Django 5.1 on 2024-12-01 12:59

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0073_alter_artwork_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='artwork',
            name='product_cat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.catalogue'),
        ),
        migrations.AlterField(
            model_name='artwork',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]