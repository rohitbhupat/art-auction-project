# Generated by Django 5.1 on 2024-12-02 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0077_alter_artwork_product_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='product_id',
            field=models.CharField(default='', max_length=255),
        ),
    ]