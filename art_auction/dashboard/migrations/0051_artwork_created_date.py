# Generated by Django 5.0.6 on 2024-07-07 06:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0050_rename_first_name_query_full_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='created_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
