# Generated by Django 5.0.6 on 2024-05-11 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_product_end_date'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Category',
            new_name='Catalogue',
        ),
        migrations.AlterField(
            model_name='product',
            name='end_date',
            field=models.DateField(),
        ),
    ]