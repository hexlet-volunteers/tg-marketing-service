from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import View
from inertia import render as inertia_render

from apps.parser.models import TelegramChannel
from config.mixins import UserAuthenticationCheckMixin

from apps.group_channels.forms import (
    AddChannelForm,
    CreateGroupForm,
    UpdateGroupForm
)
from apps.group_channels.models import Group

# константа для дефолтной аватарки
DEFAULT_AVATAR_GROUP = f'{settings.BASDIR_URL}default_avatar_group.jpg'


class CreateGroupView(View):
    def post(self, request, *args, **kwargs):
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            if not group.image_url or not group.image_url.strip():
                group.image_url = DEFAULT_AVATAR_GROUP
                group.owner = request.user
            group.save()
            return inertia_render(request, 'Channels', props={
                "flash": {
                    "success": 'Группа успешно создана'
                },
                "group": {
                    "name": group.name
                }
            }, url='/profile')
        return inertia_render(request, 'Profile', props={
            "form": {
                "name": form.data.get("name", ""),
                "description": form.data.get("description", ""),
                "image_url": form.data.get("image_url", "")
            },
            "errors": form.errors
        })


class UpdateGroupView(View):
    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        group = get_object_or_404(Group, slug=slug)
        form = UpdateGroupForm(request.POST, instance=group)

        if form.is_valid():
            form.save()
            return inertia_render(request, 'Profile', props={
                "flash": {"success": 'Группа успешно изменена'}
            })
        return inertia_render(request, 'Profile', props={
            "form": {
                "name": form.data.get("name"),
                "description": form.data.get("description"),
                "image_url": request.POST.get("image_url", ""),
            },
            "errors": form.errors
        })


class DeleteGroupView(View):
    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        group = get_object_or_404(Group, slug=slug)
        group.delete()
        return inertia_render(request, 'Profile', props={
                "flash": {"success": 'Группа успешно удалена'}
            })


class GroupDetailView(View):
    
    """
    Методы:
    group.get_data выводит данные:
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'owner': self.owner.username,
            'is_editorial': self.is_editorial,
            'order': self.order,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
    
    channels.get_data выводит данные:
            'id': self.channel_id,
            'username': self.username,
            'title': self.title,
            'description': self.description,
            'participants_count': self.participants_count,
            'parsed_at': self.parsed_at,
            'pinned_messages': self.pinned_messages,
            'creation_date': self.creation_date,
            'last_messages': self.last_messages,
            'average_views': self.average_views,
            'category': self.category,
            'country': self.country,
            'language': self.language
    """
    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        group = get_object_or_404(Group, slug=slug)

        channels = group.channels.all()

        auto_category = None
        if hasattr(group, 'auto_rule'):
            auto_category = group.auto_rule.category
            channels = TelegramChannel.objects.filter(category=auto_category)

        is_owner = request.user.is_authenticated and (group.owner == request.user)
        add_form = None
        if is_owner and not hasattr(group, 'auto_rule'):
            free_qs = TelegramChannel.objects.exclude(groups=group)
            add_form = AddChannelForm(channel_qs=free_qs)

        return inertia_render(request, 'GroupDetail', props={
            'group': group.get_data,
            'channels': channels.get_data,
            'auto_category': auto_category,
            'add_form': add_form,
            'is_owner': is_owner,
        })


class AddChannelsView(UserAuthenticationCheckMixin, UserPassesTestMixin, View):
    
    # Кажеться это лишнее так как реализована аутентификайия с использованием django-guardian
    def test_func(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return self.group.owner == self.request.user

    # На стороне фронта нет компонента groep_detaile, бронируем название компонента GroupDetail
    def post(self, request, slug):
        free_qs = TelegramChannel.objects.exclude(groups=self.group)
        form = AddChannelForm(
            request.POST,
            instance=self.group,
            channel_qs=free_qs
        )

        if form.is_valid():
            self.group.channels.add(*form.cleaned_data['channels'])
            return inertia_render(request, 'GroupDetail', props={
                "flash": {"success": 'Каналы добавлены'}
            })
        return inertia_render(request, 'GroupDetail', props={
            "form": {
                "errors": form.errors,
                "values": form.data
            }
        })
