# Generated by Django 4.2.4 on 2024-07-27 06:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("case_details", "0007_alter_cc_person_cc_gov_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="driver",
            name="case_status",
            field=models.IntegerField(choices=[(0, "Open"), (1, "Closed")], default=0),
        ),
    ]
