import logging

from telethon import TelegramClient

from apps.parser.models import TelegramChannel

log = logging.getLogger(__name__)


class BaseParser:
    """Базовый класс для всех парсеров."""

    def __init__(self, client: TelegramClient):
        self.client = client

    async def get_channel_entity(self, url: str):
        """Получить сущность канала."""
        return await self.client.get_entity(url)

    async def save_channel_model(
        self, channel_entity, data: dict
    ) -> TelegramChannel:
        """Создать/обновить модель TelegramChannel."""
        channel, created = await TelegramChannel.objects.aget_or_create(
            channel_id=channel_entity.id,
            defaults={
                "title": channel_entity.title,
                "username": channel_entity.username or "-",
                "creation_date": channel_entity.date,
                "is_public": False,
            },
        )
        return channel
