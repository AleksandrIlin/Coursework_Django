from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser


class RegisterUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text="Необязательное поле для ввода. " "Введите ваш номер телефона.",
    )
    username = forms.CharField(max_length=50, required=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "avatar",
            "first_name",
            "phone_number",
            "password1",
            "password2",
            "country",
        )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        first_name = cleaned_data.get("first_name")

        if username.lower() and first_name.lower() in [
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
            self.add_error("username", "запрещенное слово")
            self.add_error("first_name", "запрещенное слово")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр")
        return phone_number

    def clean_avatar(self):
        cleaned_data = super().clean()
        avatar = cleaned_data.get("image")

        if avatar is None:
            return None

        if avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Размер файла не должен превышать 5MB.")

        if not avatar.name.endswith(("jpg", "jpeg", "png")):
            raise forms.ValidationError(
                "Формат файла не соответствует требованиям. " "Формат файла должен быть *.jpg, *.jpeg, *.png"
            )

        return avatar


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "username",
            "avatar",
            "first_name",
            "phone_number",
            "country",
        ]
        exclude = (
            "is_blocked",
            "owner",
        )
