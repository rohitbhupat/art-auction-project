# Generated by Django 5.1 on 2024-10-01 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0061_alter_artwork_is_sold'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.CharField(choices=[('Poor', 'Poor'), ('Fair', 'Fair'), ('Good', 'Good'), ('Very Good', 'Very Good'), ('Excellent', 'Excellent')], max_length=10)),
                ('feedback_text', models.TextField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
