from django import forms

from apps.parser.models import TelegramChannel

# from config.channel.models import Channel
from apps.group_channels.models import Group


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

    def __init__(self, *args, channel_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["channels"].queryset = (
            channel_qs
            if channel_qs is not None
            else TelegramChannel.objects.all()
        )

    def clean_channels(self):
        data = self.cleaned_data["channels"]
        if not data:
            raise forms.ValidationError("Нужно выбрать минимум один канал.")
        return data
