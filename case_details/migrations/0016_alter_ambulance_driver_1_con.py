# Generated by Django 5.1.1 on 2024-09-12 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case_details', '0015_ambulance_driver_1_con_driver_amb_con'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ambulance',
            name='driver_1_con',
            field=models.BooleanField(default=1),
        ),
    ]