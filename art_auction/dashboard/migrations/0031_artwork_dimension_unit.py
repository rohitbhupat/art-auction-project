# Generated by Django 5.0.6 on 2024-06-02 11:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0030_alter_artwork_foot_alter_artwork_inches'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='dimension_unit',
            field=models.CharField(choices=[('cm', 'Centimeters'), ('ft', 'Feet')], default=django.utils.timezone.now, max_length=2),
            preserve_default=False,
        ),
    ]