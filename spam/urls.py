from django.urls import path
from django.views.decorators.cache import cache_page
from spam.apps import SpamConfig
from spam.views import (
    BlockMailingView,
    HomePageView,
    MailingAttemptListView,
    MailingClearAttemptsView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingStartView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    RecipientCreateView,
    RecipientDeleteView,
    RecipientDetailView,
    RecipientListView,
    RecipientUpdateView,
    UserMailingStatisticsView,
)

app_name = SpamConfig.name


urlpatterns = [
    path("home/", HomePageView.as_view(), name="home"),
    path("message_list/", cache_page(30)(MessageListView.as_view()), name="message_list"),
    path("message_create/", MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>/update", MessageUpdateView.as_view(), name="message_update"),
    path("message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("message/<int:pk>/detail/", MessageDetailView.as_view(), name="message_detail"),
    path("recipient/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipient/", cache_page(30)(RecipientListView.as_view()), name="recipient_list"),
    path("recipient_form/", RecipientCreateView.as_view(), name="recipient_form"),
    path(
        "recipient/update/<int:pk>/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipient/<int:pk>/delete",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path("mailing_list/", cache_page(30)(MailingListView.as_view()), name="mailing_list"),
    path("mailing_create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/update", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/delete", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path(
        "mailing_attempt_list/",
        MailingAttemptListView.as_view(),
        name="mailing_attempt_list",
    ),
    path(
        "mailing/<int:mailing_id>/start/",
        MailingStartView.as_view(),
        name="mailing_start",
    ),
    path(
        "clear-mailing-attempts/",
        MailingClearAttemptsView.as_view(),
        name="clear_mailing_attempts",
    ),
    path("user/statistics/", UserMailingStatisticsView.as_view(), name="user_statistics"),
    path(
        "mailing/<int:mailing_id>/block/",
        BlockMailingView.as_view(),
        name="mailing_block",
    ),
]
