# Generated by Django 5.0.6 on 2024-06-02 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0024_artwork_length_cm_artwork_length_ft_artwork_width_cm_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='artwork',
            old_name='length_cm',
            new_name='length_in_centimeters',
        ),
        migrations.RenameField(
            model_name='artwork',
            old_name='length_ft',
            new_name='length_in_foot',
        ),
        migrations.RenameField(
            model_name='artwork',
            old_name='width_cm',
            new_name='width_in_centimeters',
        ),
        migrations.RenameField(
            model_name='artwork',
            old_name='width_ft',
            new_name='width_in_foot',
        ),
    ]