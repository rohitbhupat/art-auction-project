# Generated by Django 5.0.6 on 2024-06-05 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0032_alter_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='last_bid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='artwork',
            name='total_bids',
            field=models.IntegerField(default=0),
        ),
    ]