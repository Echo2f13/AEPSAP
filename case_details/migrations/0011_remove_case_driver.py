# Generated by Django 4.2.4 on 2024-07-27 20:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("case_details", "0010_hospital_address"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="case",
            name="driver",
        ),
    ]
