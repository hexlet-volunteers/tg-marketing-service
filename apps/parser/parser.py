import asyncio
import logging
from random import uniform
from typing import Any, Dict

from telethon import TelegramClient
from telethon.errors import (
    AuthKeyError,
    ChannelInvalidError,
    FloodWaitError,
    UsernameNotOccupiedError,
)

from apps.parser.models import TelegramChannel
from apps.parser.parsers.channel import ChannelParser
from apps.parser.parsers.posts import PostsParser
from apps.parser.types import (
    ParsedChannelResult,
    build_parsed_channel_result,
)

log = logging.getLogger(__name__)


async def tg_parser(
    url: str,
    client: TelegramClient,  # Теперь принимаем готовый клиент
    limit: int = 10,
) -> ParsedChannelResult:
    """Основная функция парсинга Telegram-канала.

    Args:
        url: URL канала (например, "https://t.me/example_channel")
        client: Уже инициализированный и подключенный TelegramClient
        limit: Количество постов для парсинга

    Returns:
        Dict: Результаты парсинга, включая метаданные канала
              и статистику постов.
    """

    data: Dict[str, Any] = {"pinned_messages": []}

    # передается извне (из tasks.py)

    try:
        # Проверяем, подключен ли клиент, если нет — подключаем
        if not client.is_connected():
            await client.connect()

        log.info("Telegram client is ready for parsing")

        try:
            # Парсинг канала
            channel_parser = ChannelParser(client)
            channel_data = await channel_parser.parse_channel(url)
            data.update(channel_data)

            # Поиск модели канала в Django
            django_channel = await TelegramChannel.objects.aget(
                channel_id=channel_data["channel_id"]
            )

            # Парсинг постов
            posts_parser = PostsParser(client)
            posts_data = await posts_parser.parse_posts(
                channel_entity=await client.get_entity(url),
                channel_model=django_channel,
                limit=limit,
            )
            data.update(posts_data)

            log.info(
                f"Successfully parsed channel {channel_data['title']} "
                f"({channel_data['username']})"
            )
            return build_parsed_channel_result(data)

        except FloodWaitError as e:
            wait_time = e.seconds + uniform(1.0, 2.0)  # noqa: S311  # jitter
            log.error(f"FloodWaitError: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            raise

        except (ChannelInvalidError, UsernameNotOccupiedError):
            log.error(f"Invalid channel URL: {url}")
            raise

        except Exception as e:
            log.error(f"Unexpected error parsing {url}: {str(e)}")
            raise

    except AuthKeyError:
        log.critical("AUTH SESSION FAILURE — Telegram auth key invalid")
        raise
