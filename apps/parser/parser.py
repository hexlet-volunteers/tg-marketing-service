import asyncio
import logging
import random
import time

from telethon import TelegramClient
from telethon.errors import (
    AuthKeyError,
    ChannelInvalidError,
    FloodWaitError,
    ForbiddenError,
    UsernameNotOccupiedError,
)
from telethon.tl.functions.channels import GetFullChannelRequest

log = logging.getLogger(__name__)


async def tg_parser(url: str, client: TelegramClient, limit: int = 10) -> dict:
    """
    Telegram channel parser function. Retrieves channel data including:
    name, ID, description, subscriber count, pinned message, and recent posts.

    Parameters:
        url (str): URL of the Telegram channel in any valid format
                   (e.g., `https://t.me/example`, `t.me/example`, `@example`, `example`)
        client (TelegramClient): A Telegram client instance from the `telethon` library
        limit (int): Number of messages to parse (default: 10)

    Returns:
        data (dict): A dictionary containing the parsed Telegram channel data

    Note:
        This function requires a registered Telegram API application to work.
    """
    data = {}
    full_channel = None
    pinned_messages = None

    try:
        # Anti-flood - remove when dedicated number is assigned
        time.sleep(1)
        # Gets channel information
        channel = await client.get_entity(url)

        data["title"] = channel.title  # Channel title
        data["channel_id"] = channel.id  # Channel id
        data["username"] = (
            channel.username if channel.username else "-"
        )  # Channel username
        data["verified"] = channel.verified  # Is channel verified? (boolean)
        # Channel creation date
        data["creation_date"] = (
            channel.date.isoformat() if channel.date else None
        )
        # Fetches last channel posts

        last_messages = await client.get_messages(channel, limit=limit * 3)
        # Calculates average views of recent posts
        data["last_messages"] = [
            {
                "post_id": post.id,
                "post_text": post.text,
                "post_views": post.views,
            }
            for post in last_messages[:limit]
        ]
        total_views = 0
        total_posts = 0

        for post in last_messages:
            if post.views:
                total_views += post.views
                total_posts += 1
        average_views = total_views // total_posts
        data["average_views"] = average_views

    except FloodWaitError as e:
        log.error("Anti-flood triggered, waiting required")
        # wait recommended time + random interval

        await asyncio.sleep(e.seconds + random.uniform(1.0, 2.0))

    except ChannelInvalidError:
        log.warning(f"This channel is private or unavailable: {url}")

    except UsernameNotOccupiedError:
        log.error(f"Username does not exist: {url}")

    except AuthKeyError:
        log.critical("AUTH SESSION FAILURE")

    except Exception as e:
        log.error(f"ERROR - {e}")

    if channel:
        try:
            # Fetch complete channel information
            full_channel = await client(GetFullChannelRequest(channel))

        except FloodWaitError as e:
            log.error("Anti-flood triggered, waiting required")
            # wait recommended time + random interval
            await asyncio.sleep(e.seconds + random.uniform(1.0, 2.0))

        except ForbiddenError:
            log.warning("Failed to access full channel information")

        except Exception as e:
            log.error(f"ERROR - {e}")

        if full_channel:
            # Fetching channel participants count
            participants_count = full_channel.full_chat.participants_count
            data["participants_count"] = (
                participants_count if participants_count else "Нет участников"
            )
            # Fetching channel description
            description = full_channel.full_chat.about
            data["description"] = description if description else "Нет описания"
            # Fetchin pinned message id
            pinned_message_id = full_channel.full_chat.pinned_msg_id
            # Fetching pinned message
            if pinned_message_id:
                pinned_messages = await client.get_messages(
                    channel, ids=pinned_message_id
                )
            data["pinned_messages"] = [
                {
                    "text": pinned_messages.message
                    if pinned_messages
                    else "Нет закрепленного сообщения",
                    "id": pinned_message_id if pinned_messages else None,
                }
            ]

    log.debug(f"Channel successfully parsed: {data}")
    return data
