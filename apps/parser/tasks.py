import asyncio
import logging
import random
import time

from asgiref.sync import sync_to_async
from celery import shared_task
from django.conf import settings
from django.db import DatabaseError, IntegrityError
from django.utils import timezone
from telethon import TelegramClient
from telethon.sessions import StringSession

from apps.parser.models import ChannelStats, TelegramChannel
from apps.parser.parser import tg_parser

log = logging.getLogger(__name__)


@shared_task
def parse_channel(channel_id):
    """Celery task for channel parse"""
    try:
        channel = TelegramChannel.objects.get(channel_id=channel_id)
    except TelegramChannel.DoesNotExist:
        log.error(f"Channel with ID {channel_id} does not exist in database")
        return
    except DatabaseError as e:
        log.error(f"Database error while fetching channel -;{channel_id} - {e}")
        return

    async def run_parser(channel_obj):
        """Secondary func for async parsing"""
        async with TelegramClient(
            StringSession(settings.TELEGRAM_SESSION_STRING),
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
        ) as client:
            try:
                # make connection with Telegram
                await client.connect()
                data = await tg_parser(channel_obj.username, client)
                # using sync_to_async to avoid Django ORM errors (cause ORM is sync)
                await sync_to_async(save_channel_data)(channel_obj, data)
                await sync_to_async(save_channel_stats)(channel_obj, data)
            except (DatabaseError, IntegrityError) as e:
                log.error(
                    f"Database safe error for {channel_obj.username} - {e}"
                )
            except Exception as e:
                log.error(f"Unexpected error: - {e}", exc_info=True)

    try:
        asyncio.run(run_parser(channel))
    except ConnectionError as e:
        log.error(f"Connection failed for {channel_id}: {e}")


def save_channel_data(channel, data):
    """Save channels data"""
    channel.title = data["title"]
    channel.description = data.get("description", "Нет описания")
    channel.participants_count = data.get("participants_count", 0)
    channel.pinned_messages = data.get("pinned_messages", [])
    channel.last_messages = data.get("last_messages", [])
    channel.average_views = data.get("average_views", 0)
    channel.parsed_at = timezone.now()
    channel.save()
    log.info(f"Data from channel {channel.title} successfully saved")


def save_channel_stats(channel, data):
    """Save channel stats"""
    last_stats = (
        ChannelStats.objects.filter(channel=channel)
        .order_by("-parsed_at")
        .first()
    )
    current_date = timezone.now()
    current_count = data.get("participants_count", 0)

    # daily growth for participants
    if last_stats and last_stats.parsed_at.date() != current_date.date():
        daily_growth = current_count - last_stats.participants_count
    else:
        daily_growth = last_stats.daily_growth if last_stats else 0

    ChannelStats.objects.create(
        channel=channel,
        participants_count=current_count,
        daily_growth=daily_growth,
        parsed_at=current_date,
    )
    log.info(
        f"Stats for channel {channel.title} saved: participants={current_count}, growth={daily_growth}"
    )


@shared_task
def parse_all_channels():
    """Task for Celery: parse all channels from database"""
    channels = TelegramChannel.objects.all()
    if not channels:
        log.warning("There are no channels")
        return

    for channel in channels:
        # start task for parsing
        parse_channel.delay(channel.channel_id)
        # add pause between parsing, 15s + random value
        pause = 15 + random.uniform(0, 5)
        log.info(
            f"Started task for channel {channel.channel_id}, next one in {pause:.2f} s"
        )
        time.sleep(pause)
