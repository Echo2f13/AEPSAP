# Generated by Django 4.2.4 on 2024-07-27 18:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("case_details", "0009_remove_cc_person_cc_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="hospital",
            name="address",
            field=models.CharField(max_length=1500, null=True),
        ),
    ]
