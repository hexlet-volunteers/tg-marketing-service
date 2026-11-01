from typing import Any

from django import forms
from django.db.models import QuerySet

# from config.channel.models import Channel
from apps.group_channels.models import Group
from apps.parser.models import TelegramChannel
from apps.users.validators import validate_http_url


class CreateGroupForm(forms.ModelForm):
    name = forms.CharField(
        max_length=150,
        required=True,
        label="Название группы",
        widget=forms.TextInput(
            attrs={
                "id": "groupName",
                "class": "form-control",
                "autofocus": True,
                "name": "name",
            }
        ),
    )
    description = forms.CharField(
        required=False,
        label="Описание",
        widget=forms.Textarea(
            attrs={
                "id": "groupDescription",
                "class": "form-control",
                "rows": 3,
                "name": "description",
            }
        ),
    )
    image_url = forms.CharField(
        required=False,
        validators=[validate_http_url],
        label="Изображение (URL)",
        widget=forms.URLInput(
            attrs={
                "id": "groupImage",
                "placeholder": "https://example.com/image.jpg",
                "class": "form-control",
                "name": "image_url",
            }
        ),
    )

    class Meta:
        model = Group
        fields = (
            "name",
            "description",
            "image_url",
        )


class UpdateGroupForm(forms.ModelForm):
    name = forms.CharField(
        max_length=150,
        required=True,
        label="Название группы",
        widget=forms.TextInput(
            attrs={
                "id": "editGroupName",
                "class": "form-control",
                "autofocus": True,
                "name": "name",
            }
        ),
    )
    description = forms.CharField(
        required=False,
        label="Описание",
        widget=forms.Textarea(
            attrs={
                "id": "editGroupDescription",
                "class": "form-control",
                "rows": 3,
                "name": "description",
            }
        ),
    )
    image_url = forms.CharField(
        required=False,
        validators=[validate_http_url],
        label="Изображение (URL)",
        widget=forms.URLInput(
            attrs={
                "id": "editGroupImage",
                "placeholder": "https://example.com/image.jpg",
                "class": "form-control",
                "name": "image_url",
            }
        ),
    )

    class Meta:
        model = Group
        fields = (
            "name",
            "description",
            "image_url",
        )


class AddChannelForm(forms.ModelForm):
    channels = forms.ModelMultipleChoiceField(
        queryset=TelegramChannel.objects.none(),
        label="Добавить каналы",
        widget=forms.SelectMultiple(
            attrs={
                "id": "groupChannels",
                "class": "form-select",
                "size": 10,
                "name": "channels",
            }
        ),
        required=True,
        help_text="Удерживайте Ctrl/Cmd, чтобы выбрать несколько",
    )

    class Meta:
        model = Group
        fields = ("channels",)

    def __init__(
        self,
        *args: Any,
        channel_qs: QuerySet[TelegramChannel] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        channels_field = self.fields["channels"]
        if isinstance(channels_field, forms.ModelMultipleChoiceField):
            channels_field.queryset = (
                channel_qs
                if channel_qs is not None
                else TelegramChannel.objects.all()
            )

    def clean_channels(self) -> QuerySet[TelegramChannel]:
        data = self.cleaned_data["channels"]
        if not data:
            raise forms.ValidationError("Нужно выбрать минимум один канал.")
        return data
