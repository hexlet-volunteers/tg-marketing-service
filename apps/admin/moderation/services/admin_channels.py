from typing import cast

from asgiref.sync import async_to_sync
from django.db import IntegrityError, transaction
from django.utils import timezone
from telethon import TelegramClient
from telethon.sessions import StringSession

from apps.admin.moderation.dto.admin_channels_dto import (
    AdminChannelData,
    AdminChannelsDTO,
)
from apps.admin.moderation.models import ModerationRequest
from apps.admin.moderation.services.moderation import ModerationService
from apps.parser.forms import ChannelParseForm
from apps.parser.models import TelegramChannel
from apps.parser.utils import get_telegram_credentials
from apps.users.models import User


class AdminChannelsService:
    """Подготавливает список одобренных каналов для админки."""

    @staticmethod
    def get_channels() -> list[TelegramChannel]:
        return list(
            TelegramChannel.objects.filter(
                moderation_requests__status="approved"
            )
            .distinct()
            .order_by("title", "channel_id")
        )

    @staticmethod
    def get_categories() -> list[str]:
        choices = cast(
            list[tuple[str, str]],
            getattr(
                ChannelParseForm.base_fields["category"],
                "choices",
            ),
        )
        return [
            value
            for value, _label in choices
            if value not in ("Выберите категорию...", "Все категории")
        ]

    @classmethod
    def update_category(cls, channel_id: int, category: str) -> None:
        if category not in cls.get_categories():
            raise ValueError("Недопустимая категория")

        channel = TelegramChannel.objects.get(channel_id=channel_id)
        channel.category = category
        channel.save(update_fields=["category"])

    @staticmethod
    def toggle_verified(channel_id: int) -> None:
        channel = TelegramChannel.objects.get(channel_id=channel_id)
        channel.is_verified = not channel.is_verified
        channel.verified_at = timezone.now() if channel.is_verified else None
        channel.save(update_fields=["is_verified", "verified_at"])

    @staticmethod
    def _fetch_channel(identifier: str) -> dict:
        api_id, api_hash, session_string = get_telegram_credentials(
            require_session=True
        )

        async def fetch() -> dict:
            client = TelegramClient(
                StringSession(session_string),
                api_id,
                api_hash,
            )
            await client.connect()
            try:
                entity = await client.get_entity(identifier.strip())
                return {
                    "channel_id": entity.id,
                    "title": entity.title,
                    "username": entity.username or "",
                }
            finally:
                await client.disconnect()

        return async_to_sync(fetch)()

    @classmethod
    def add_channel(
        cls,
        identifier: str,
        category: str,
        admin: User,
    ) -> TelegramChannel:
        identifier = identifier.strip()
        if not identifier:
            raise ValueError("Укажите username или ссылку на канал")

        if category not in cls.get_categories():
            raise ValueError("Недопустимая категория")

        channel_data = cls._fetch_channel(identifier)
        username = (channel_data["username"] or "").strip().lstrip("@")

        if not username:
            raise ValueError("У канала должен быть публичный username")

        if ModerationService._find_duplicate(None, username):
            raise ValueError("Канал с таким username уже существует")

        try:
            with transaction.atomic():
                channel = TelegramChannel.objects.create(
                    channel_id=channel_data["channel_id"],
                    username=username,
                    title=channel_data["title"],
                    category=category,
                )

                ModerationRequest.objects.create(
                    submitted_by=admin,
                    channel_identifier=identifier,
                    channel_by=channel,
                    category=category,
                    country="",
                    language="",
                    status="approved",
                    moderator=admin,
                    resolved_at=timezone.now(),
                )
        except IntegrityError as exc:
            raise ValueError(
                "Канал с таким username или ID уже существует"
            ) from exc

        return channel

    @classmethod
    def build_dto(cls) -> AdminChannelsDTO:
        channels = [
            AdminChannelData(
                channelId=channel.channel_id,
                username=channel.username or "",
                title=channel.title,
                category=channel.category or "",
                isVerified=channel.is_verified,
                subscribers=channel.participants_count,
            )
            for channel in cls.get_channels()
        ]

        return AdminChannelsDTO(
            channels=channels,
            categories=cls.get_categories(),
        )
