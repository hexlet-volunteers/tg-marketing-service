from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm,
)
from django.utils.crypto import get_random_string

from apps.users.models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]

    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "class": "form-control",
                "placeholder": "Имя пользователя",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "form-control",
                "placeholder": "Пароль",
            }
        ),
    )


class UserRegForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "password1",
            "password2",
            "email",
            "bio",
            "avatar_image",
        )

    first_name = forms.CharField(
        required=False,
        label="Имя",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Имя"}
        ),
    )
    last_name = forms.CharField(
        required=False,
        label="Фамилия",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Фамилия"}
        ),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Пароль"}
        ),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "form-control",
                "placeholder": "Подтверждение пароля",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
    )
    bio = forms.CharField(
        required=False,
        label="О себе",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "О себе",
                "rows": 3,
            }
        ),
    )
    terms = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )
    avatar_image = forms.CharField(
        required=False,
        label="URL аватара",
        widget=forms.TextInput(
            attrs={"name": "avatar_image", "class": "form-control"}
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return email

    def _generate_username(self):
        email_local_part = self.cleaned_data["email"].split("@", 1)[0]
        username_base = "".join(
            char if char.isalnum() or char in "@.+-_" else "_"
            for char in email_local_part
        ).strip("._-+")
        username_base = (username_base or "user")[:140]

        while True:
            username = f"{username_base}_{get_random_string(8)}"
            if not User.objects.filter(username=username).exists():
                return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self._generate_username()
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "password1",
            "password2",
            "email",
            "bio",
            "avatar_image",
        )

    first_name = forms.CharField(
        label="Имя",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Имя"}
        ),
    )
    last_name = forms.CharField(
        label="Фамилия",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Фамилия"}
        ),
    )
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "class": "form-control",
                "placeholder": "Имя пользователя",
            }
        ),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Пароль"}
        ),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "form-control",
                "placeholder": "Подтверждение пароля",
            }
        ),
    )
    email = forms.CharField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
    )
    bio = forms.CharField(
        required=False,
        label="О себе",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "О себе",
                "rows": 3,
            }
        ),
    )
    avatar_image = forms.CharField(
        required=False,
        label="URL аватара",
        widget=forms.TextInput(
            attrs={"name": "avatar_image", "class": "form-control"}
        ),
    )


class AvatarChange(UserChangeForm):
    class Meta:
        model = User
        fields = ("avatar_image",)
        avatar_image = forms.CharField(
            required=False,
            label="URL аватара",
            widget=forms.TextInput(
                attrs={
                    "id": "avatarUrl",
                    "name": "avatar_image",
                    "class": "form-control",
                    "placeholder": "https://example.com/avatar.jpg",
                }
            ),
        )


class RestorePasswordRequestForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Пожалуйста, введите ваш email",
            }
        ),
    )


class RestorePasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Новый пароль"}
        ),
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Подтверждение пароля",
            }
        ),
    )
