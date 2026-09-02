import re
from typing import List

from telethon import TelegramClient
from telethon.tl.types import Channel, Message

from apps.parser.models import Post, PostReaction, TelegramChannel
from apps.parser.types import ParsedPostsData


class PostsParser:
    """Парсер постов и реакций."""

    def __init__(self, client: TelegramClient):
        self.client = client

    async def parse_posts(
        self,
        channel_entity: "Channel",
        channel_model: TelegramChannel,
        limit: int = 10,
    ) -> ParsedPostsData:
        """Парсинг постов и реакций."""
        messages: List[Message] = await self.client.get_messages(
            channel_entity, limit=limit * 3
        )
        total_views = 0
        total_comments = 0
        total_reposts = 0
        post_count = 0

        for message in messages[:limit]:
            if message.service:
                continue

            # Обработка поста
            permalink = (
                f"https://t.me/{channel_entity.username}/{message.id}"
                if channel_entity.username
                else None
            )

            current_forwards = message.forwards or 0
            current_comments = message.replies.replies if message.replies else 0
            current_views = message.views or 0

            fwd_from = None
            if message.fwd_from:
                # Проверяем, является ли источник каналом
                if hasattr(message.fwd_from, "channel_id"):
                    fwd_from = message.fwd_from.channel_id
                elif hasattr(message.fwd_from, "sender_id"):
                    fwd_from = message.fwd_from.sender_id

            mentions = []
            if message.text:
                # Паттерны упоминаний каналов (поддержка точек и подчеркиваний)
                found_mentions = re.findall(r"@([\w\.]+)", message.text)
                mentions = list(set(found_mentions))

            # 1. Создание или получение поста
            post, created = await Post.objects.aget_or_create(
                channel=channel_model,
                telegram_message_id=message.id,
                defaults={
                    "text": message.text or "",
                    "published_at": message.date,
                    "views": current_views,
                    "permalink": permalink,
                    "forwards": current_forwards,
                    "comments_count": current_comments,
                    "fwd_from": fwd_from,
                    "mentions": mentions,
                },
            )

            # 2. Обновление полей для существующих постов
            if not created:
                update_fields = []

                if current_views > post.views:
                    post.views = current_views
                    update_fields.append("views")

                if current_forwards > post.forwards:
                    post.forwards = current_forwards
                    update_fields.append("forwards")

                if current_comments > post.comments_count:
                    post.comments_count = current_comments
                    update_fields.append("comments_count")

                if fwd_from != post.fwd_from:
                    post.fwd_from = fwd_from
                    update_fields.append("fwd_from")

                if mentions != post.mentions:
                    post.mentions = mentions
                    update_fields.append("mentions")

                if update_fields:
                    await post.asave(update_fields=update_fields)

            # 3. Обработка реакций
            await PostReaction.objects.filter(post=post).adelete()

            if message.reactions:
                for reaction in message.reactions.results:
                    # reaction.reaction — это объект типа ReactionEmoji
                    emoji = getattr(
                        reaction, "emoticon", str(reaction.reaction)
                    )
                    await PostReaction.objects.acreate(
                        post=post,
                        emoji=emoji,
                        count=reaction.count,
                    )

            # Сбор статистики для возвращаемого агрегата
            if current_views:
                total_views += current_views
            if current_comments:
                total_comments += current_comments
            if current_forwards:
                total_reposts += current_forwards
            post_count += 1

        return {
            "total_posts": post_count,
            "average_views": total_views // max(post_count, 1),
            "average_comments": total_comments // max(post_count, 1),
            "average_reposts": total_reposts // max(post_count, 1),
        }
