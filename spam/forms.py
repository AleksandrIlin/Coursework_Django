from django import forms

from .models import Mailing, Message, Recipient


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comment"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get("subject")
        body = cleaned_data.get("body")

        if subject.lower() and body.lower() in [
            "казино",
            "криптовалюта",
            "крипта",
            "биржа",
            "дешево",
            "бесплатно",
            "обман",
            "полиция",
            "радар",
        ]:
            self.add_error("subject", "запрещенное слово")
            self.add_error("body", "запрещенное слово")


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["first_send_time", "end_time", "message", "recipients", "status"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
