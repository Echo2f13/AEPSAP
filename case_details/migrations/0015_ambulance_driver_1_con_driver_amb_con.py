# Generated by Django 5.1.1 on 2024-09-12 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case_details', '0014_driver_is_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='ambulance',
            name='driver_1_con',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='driver',
            name='amb_con',
            field=models.BooleanField(default=0),
        ),
    ]
