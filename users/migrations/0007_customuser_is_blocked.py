# Generated by Django 5.1.1 on 2024-11-04 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_alter_customuser_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="is_blocked",
            field=models.BooleanField(default=False),
        ),
    ]
