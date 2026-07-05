import logging

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView
from inertia import render as inertia_render
from telethon import TelegramClient
from telethon.sessions import StringSession

from apps.parser.forms import ChannelParseForm
from apps.parser.models import ChannelStats, TelegramChannel
from apps.parser.parser import tg_parser
from config.mixins import UserAuthenticationCheckMixin

log = logging.getLogger(__name__)


class ParserView(UserAuthenticationCheckMixin, FormView):
    form_class = ChannelParseForm
    template_name = 'parser/parse_channel.html'
    success_url = reverse_lazy("parser:list")

    def get_telegram_client(self):
        """Get Telegram client for parser work"""
        if not settings.TELEGRAM_SESSION_STRING:
            raise ImproperlyConfigured(
                'TELEGRAM_SESSION_STRING\
                    (needed by Telethon to parse data from Telegram)\
                        is not set. Please run\
                            `uv run python3 manage.py set_sessions_string`'
            )
        return TelegramClient(
            StringSession(settings.TELEGRAM_SESSION_STRING),
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
        )

    async def async_tg_parser(self, url, limit=10):
        """Parser wrapper"""
        client = self.get_telegram_client()
        await client.connect()
        try:
            return await tg_parser(url, client, limit)
        finally:
            await client.disconnect()
    
    def save_channel(self, data, request=None):
        """Create or update channel"""
        channel, created = TelegramChannel.objects.update_or_create(
            channel_id=data["channel_id"],
            defaults={
                'title': data['title'],
                'username': data['username'],
                'description': data['description'],
                'participants_count': data['participants_count'],
                'pinned_messages': data['pinned_messages'],
                'last_messages': data['last_messages'],
                'average_views': data['average_views'],
                'language': data['language'],
                'country': data['country'],
                'category': data['category'],
            }
        )

        if created:
            log.info(f"New channel created: {channel.title}")
        else:
            log.info(f"Channel updated: {channel.title}")

        return channel, created
            
    def save_stats(self, channel, data):
        """Create stats record with growth calculation"""
        last_stats = (
            ChannelStats.objects.filter(channel=channel).order_by("-parsed_at").first()
        )
        current_date = timezone.now()
        current_count = data["participants_count"]

        if last_stats and last_stats.parsed_at.date() != current_date.date():
            daily_growth = current_count - last_stats.participants_count
        else:
            daily_growth = last_stats.daily_growth if last_stats else 0

        # Create new statistics
        ChannelStats.objects.create(
            channel=channel,
            participants_count=current_count,
            daily_growth=daily_growth,
            parsed_at=current_date,
        )

        # Update parsing date for Telegram channel
        channel.parsed_at = current_date

        channel.save(update_fields=["parsed_at"])
        log.info(
            f"For channel: {channel.title} parsed stat; "
            f"- participants: {current_count} growth: {daily_growth}"
        )

    def form_valid(self, form):
        """ Обработка формы """
        identifier = form.cleaned_data['channel_identifier']
        limit = form.cleaned_data['limit']
        language = form.cleaned_data['language']
        country = form.cleaned_data['country']
        category = form.cleaned_data['category']
        log.info(f'Начинаем обработку данных для канала; '
                 f'- {identifier} лимит - {limit}')
        try:
            # Start async parsing function
            async_parser = async_to_sync(self.async_tg_parser)
            parsed_data = async_parser(identifier, limit)
            parsed_data.update({'language': language,
                                'country': country,
                                'category': category})

            log.info(f'Парсинг завершен для канала;'
                     f'- {parsed_data['title']} ({parsed_data['channel_id']}')

            # Saving data
            channel, created = self.save_channel(parsed_data)
            self.save_stats(channel, parsed_data)

            # Generating user message
            message = (
                f"New channel created: {channel.title}"
                if created
                else f"Channel updated: {channel.title}"
            )
            messages.success(self.request, message)

            return super().form_valid(form)

        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)


class ParserListView(ListView):
    model = TelegramChannel
    token = 'TEMP_TOKEN'

    def get(self, request, *args, **kwargs):
        channels = self.get_queryset()
    
        return inertia_render(
            request,
            'ChannelAnalytics',
            props={
                "channels": channels,
                "csrfToken": self.token, 
            }
        )


class ParserDetailView(DetailView):
    model = TelegramChannel
    template_name = 'parser/channel_detail.html'
    context_object_name = "channel"

# Create your views here.