import logging
from typing import Any

from asgiref.sync import async_to_sync
from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView, View
from inertia import render as inertia_render
from telethon import TelegramClient
from telethon.sessions import StringSession

from apps.parser.forms import ChannelParseForm
from apps.parser.models import ChannelStats, TelegramChannel
from apps.parser.parser import tg_parser
from apps.parser.utils import get_telegram_credentials
from config.mixins import UserAuthenticationCheckMixin

log = logging.getLogger(__name__)


class ParserView(UserAuthenticationCheckMixin, FormView):
    form_class = ChannelParseForm
    template_name = "parser/parse_channel.html"
    success_url = reverse_lazy("parser:list")

    def get_telegram_client(self) -> TelegramClient:
        """Get Telegram client for parser work"""
        api_id, api_hash, session_string = get_telegram_credentials(
            require_session=True
        )
        return TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash,
        )

    async def async_tg_parser(
        self, url: str, limit: int = 10
    ) -> dict[str, Any]:
        """Parser wrapper"""
        client = self.get_telegram_client()
        await client.connect()
        try:
            return await tg_parser(url, client, limit)
        finally:
            await client.disconnect()

    def save_channel(
        self, data: dict[str, Any]
    ) -> tuple[TelegramChannel, bool]:
        """Create or update channel"""
        channel, created = TelegramChannel.objects.update_or_create(
            channel_id=data["channel_id"],
            defaults={
                "title": data["title"],
                "username": data["username"],
                "description": data["description"],
                "participants_count": data["participants_count"],
                "pinned_messages": data["pinned_messages"],
                "last_messages": data["last_messages"],
                "average_views": data["average_views"],
                "language": data["language"],
                "country": data["country"],
                "category": data["category"],
            },
        )

        if created:
            log.info(f"New channel created: {channel.title}")
        else:
            log.info(f"Channel updated: {channel.title}")

        return channel, created

    def save_stats(
        self, channel: TelegramChannel, data: dict[str, Any]
    ) -> None:
        """Create stats record with growth calculation"""
        last_stats = (
            ChannelStats.objects.filter(channel=channel)
            .order_by("-parsed_at")
            .first()
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

    def form_valid(self, form: ChannelParseForm) -> HttpResponse:
        """Обработка формы"""
        identifier = form.cleaned_data["channel_identifier"]
        limit = form.cleaned_data["limit"]
        language = form.cleaned_data["language"]
        country = form.cleaned_data["country"]
        category = form.cleaned_data["category"]
        log.info(
            f"Начинаем обработку данных для канала; "
            f"- {identifier} лимит - {limit}"
        )
        try:
            # Start async parsing function
            async_parser = async_to_sync(self.async_tg_parser)
            parsed_data = async_parser(identifier, limit)
            parsed_data.update(
                {"language": language, "country": country, "category": category}
            )

            log.info(
                f"Парсинг завершен для канала: "
                f"{parsed_data['title']} ({parsed_data['channel_id']})"
            )

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
    token = "TEMP_TOKEN"

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        channels = self.get_queryset()

        return inertia_render(
            request,
            "ChannelAnalytics",
            props={
                "channels": channels,
                "csrfToken": self.token,
            },
        )


class ParserDetailView(DetailView):
    model = TelegramChannel
    template_name = "parser/channel_detail.html"
    context_object_name = "channel"


class ChannelLookupView(View):
    """
    API endpoint для поиска каналов

    GET /parser/lookup/?q=<query>

    Параметры:
    - q (str): поисковая строка по title или username

    Возвращает JSON:
    [
        {
            "id": 123456789,
            "title": "Channel Name",
            "username": "channelname",
            "participants_count": 5000,
            "category": "news"
        }
    ]

    - Пустой q / Нет совпадений - возвращает []
    - Максимум 10 результатов
    """

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> JsonResponse:
        q = request.GET.get("q", "").strip()

        if not q:
            return JsonResponse([], safe=False)

        channels = TelegramChannel.objects.filter(
            Q(title__icontains=q) | Q(username__icontains=q)
        ).order_by("-participants_count")[:10]

        result = list(
            channels.values(
                "id",
                "title",
                "username",
                "participants_count",
                "category",
            )
        )

        # Временно заглушка, пока в модели TelegramChannel нету аватарки
        for item in result:
            item["avatar"] = None

        return JsonResponse(result, safe=False)


# Create your views here.
