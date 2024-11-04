# Generated by Django 5.1.1 on 2024-11-04 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("spam", "0010_recipient_owner"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="message",
            options={
                "ordering": ["subject"],
                "permissions": [
                    ("can_view_all_mailings", "can view all mailings"),
                    ("can_disable_mailings", "can disable mailings"),
                ],
                "verbose_name": "Сообщение",
                "verbose_name_plural": "Сообщения",
            },
        ),
        migrations.AlterModelOptions(
            name="recipient",
            options={
                "ordering": ["full_name"],
                "permissions": [("can_view_all_recipients", "can view all recipients")],
                "verbose_name": "Получатель",
                "verbose_name_plural": "Получатели",
            },
        ),
    ]