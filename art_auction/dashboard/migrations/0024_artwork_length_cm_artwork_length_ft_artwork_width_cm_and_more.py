# Generated by Django 5.0.6 on 2024-06-02 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0023_payment_created_at_payment_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='length_cm',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='artwork',
            name='length_ft',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='artwork',
            name='width_cm',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='artwork',
            name='width_ft',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
