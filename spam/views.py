from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View
from spam.forms import MailingForm, MessageForm, RecipientForm
from spam.models import Mailing, MailingAttempt, Message, Recipient, UserMailingStatistics
from spam.servicies import get_mailing_from_cache, get_message_from_cache, get_recipient_from_cache
from utils.logger import setup_logging
from django.core.exceptions import PermissionDenied

setup_logging()


class HomePageView(View):
    template_name = "spam/home.html"

    def get(self, request):
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(status="Запущена").count()
        unique_recipients = Recipient.objects.distinct().count()

        context = {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "unique_recipients": unique_recipients,
        }

        return render(request, self.template_name, context)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    form_class = MailingForm
    template_name = "spam/mailing_list.html"
    context_object_name = "mailing_list"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_permission('can_view_all_mailings'):
            return get_mailing_from_cache()
        else:
            user = self.request.user
            return Mailing.objects.filter(owner=user)


class MailingCreateView(View):
    def get(self, request):
        form = MailingForm()
        return render(request, "spam/mailing_form.html", {"form": form})

    def post(self, request):
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            return redirect("spam:mailing_list")
        return render(request, "spam/mailing_form.html", {"form": form})


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "spam/mailing_form.html"
    success_url = reverse_lazy("spam:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Mailing.DoesNotExist:
            raise PermissionDenied("У Вас нет прав для редактирования этого сообщения.")


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "spam/mailing_delete.html"
    success_url = reverse_lazy("spam:mailing_list")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.has_perm("spam.delete_mailing")
            or self.request.mailing.owner
        )

    def handle_no_permission(self):
        return redirect("spam:mailing_list")

    def get_object(self, queryset=None):
        return get_object_or_404(Mailing, pk=self.kwargs["pk"])


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "spam/mailing_detail.html"
    context_object_name = "mailing"


class MailingStartView(View):

    def get(self, request, mailing_id):
        mailing = get_object_or_404(Mailing, id=mailing_id)
        return render(request, "spam/mailing_start.html", {"object": mailing})

    def post(self, request, mailing_id):
        mailing = get_object_or_404(Mailing, id=mailing_id)
        mailing.send_mailing()

        return redirect("spam:mailing_attempt_list")


class MailingClearAttemptsView(View):

    def post(self, request):
        MailingAttempt.objects.all().delete()
        return redirect("spam:mailing_attempt_list")


class MessageListView(ListView):
    model = Message
    template_name = "spam/message_list.html"
    context_object_name = "message_list"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_permission('can_view_all_messages'):
            return get_message_from_cache()
        else:
            user = self.request.user
            return Mailing.objects.filter(owner=user)


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "spam/message_from.html"
    context_object_name = "message_from"
    success_url = reverse_lazy("spam:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "spam/message_from.html"
    success_url = reverse_lazy("spam:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Message.DoesNotExist:
            raise PermissionDenied("У Вас нет прав для редактирования этого сообщения.")


class MessageDetailView(DetailView):
    model = Message
    fields = ["subject", "body"]
    template_name = "spam/message_detail.html"
    success_url = reverse_lazy("spam:message_detail")


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    template_name = "spam/message_delete.html"
    success_url = reverse_lazy("spam:message_list")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.message.owner
            and self.request.user.has_perm("spam.delete_message")
        )

    def handle_no_permission(self):
        return redirect("spam:message_list")


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = "spam/recipient_detail.html"
    context_object_name = "recipient"


class RecipientListView(ListView):
    model = Recipient
    template_name = "spam/recipient_list.html"
    context_object_name = "recipient_list"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_permission('can_view_all_recipients'):
            return get_recipient_from_cache()
        else:
            user = self.request.user
            return Mailing.objects.filter(owner=user)


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "spam/recipient_form.html"
    context_object_name = "form_recipient"
    success_url = reverse_lazy("spam:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "spam/recipient_form.html"
    success_url = reverse_lazy("spam:recipient_list")

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Recipient.DoesNotExist:
            raise PermissionDenied("У Вас нет прав для редактирования этого получателя.")


class RecipientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipient
    template_name = "spam/recipient_delete.html"
    success_url = reverse_lazy("spam:recipient_list")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.has_perm("spam.delete_recipient")
            or self.request.user.owner
        )

    def handle_no_permission(self):
        return redirect("spam:recipient_list")


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = "spam/mailing_attempt_list.html"
    context_object_name = "mailing_attempt_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailings"] = Mailing.objects.all()
        return context


class UserMailingStatisticsView(View):
    def get(self, request):
        user_stats, created = UserMailingStatistics.objects.get_or_create(user=request.user)

        return render(request, "spam/user_statistics.html", {"user_stats": user_stats})


class BlockMailingView(LoginRequiredMixin, View):

    def get(self, request, mailing_id):
        mailing = get_object_or_404(Mailing, id=mailing_id)
        return render(request, "spam/mailing_block.html", {"mailing": mailing})

    def post(self, request, mailing_id):
        mailing = get_object_or_404(Mailing, id=mailing_id)

        if not request.user.has_perm("spam.can_disable_mailings"):
            return HttpResponseForbidden("У вас нет прав для блокировки рассылки.")

        is_blocked = request.POST.get("is_blocked")
        mailing.is_blocked = is_blocked == "on"
        mailing.save()
        return redirect("spam:mailing_list")
