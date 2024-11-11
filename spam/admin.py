from django.contrib import admin
from spam.models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "comment")
    list_filter = ("full_name",)
    search_fields = (
        "email",
        "full_name",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "body")
    list_filter = ("subject",)
    search_fields = (
        "subject",
        "body",
    )


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_send_time",
        "end_time",
        "status",
        "message",
    )
    list_filter = ("status",)
    search_fields = (
        "message",
        "recipients",
    )


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt_datetime", "status", "server_response", "mailing")
    list_filter = (
        "status",
        "attempt_datetime",
    )
    search_fields = ("attempt_datetime",)
