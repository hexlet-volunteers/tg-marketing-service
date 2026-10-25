import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from apps.parser.models import Post, PostReaction, TelegramChannel
from apps.parser.parsers.posts import PostsParser


def load_fixture(name: str):
    filename = (
        name if name.startswith("model_parser_") else f"model_parser_{name}"
    )
    file_path = f"tests/fixtures/{filename}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["valid"]


@pytest.fixture
async def channel(db):
    channel, created = await TelegramChannel.objects.aget_or_create(
        channel_id=12345,
        defaults={"title": "Test Channel", "username": "testchannel"},
    )
    return channel


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def parser(mock_client):
    return PostsParser(mock_client)


@pytest.mark.django_db
class TestPostsParser:
    @pytest.mark.asyncio
    async def test_parse_posts_with_fixtures(
        self, channel, mock_client, parser
    ):
        fixture_data = load_fixture("post")
        data = fixture_data[0]

        # 1. СИНХРОНИЗАЦИЯ ТЕКСТА И МЕНШНОВ
        current_text = data["text"]
        mentions = data.get("mentions", [])

        if mentions and not any(m in current_text for m in mentions):
            current_text = f"{current_text} {' '.join(mentions)}"

        # 2. СОЗДАНИЕ MOCK-ОБЪЕКТА
        mock_message = MagicMock()
        mock_message.id = data["telegram_message_id"]
        mock_message.service = False
        mock_message.text = current_text

        if isinstance(data["published_at"], str):
            dt = datetime.fromisoformat(
                data["published_at"].replace("Z", "+00:00")
            )
        else:
            dt = data["published_at"]
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        mock_message.date = dt

        mock_message.views = data["views"]
        mock_message.forwards = data["forwards"]

        mock_replies = MagicMock()
        mock_replies.replies = data["comments_count"]
        mock_message.replies = mock_replies

        if data["fwd_from"]:
            mock_fwd_from = MagicMock()
            mock_from_id = MagicMock()
            mock_from_id.channel_id = data["fwd_from"]

            mock_fwd_from.from_id = mock_from_id
            mock_message.fwd_from = mock_fwd_from
        else:
            mock_message.fwd_from = None

        mock_message.entities = []

        reaction_data = load_fixture("post_reaction")[0]

        mock_reaction_item = MagicMock()
        mock_inner_reaction = MagicMock()
        mock_inner_reaction.emoticon = reaction_data["emoji"]

        mock_reaction_item.reaction = mock_inner_reaction
        mock_reaction_item.count = reaction_data["count"]

        mock_reactions_container = MagicMock()
        mock_reactions_container.results = [mock_reaction_item]

        mock_message.reactions = mock_reactions_container

        mock_client.get_messages.return_value = [mock_message]
        mock_channel_entity = MagicMock(username="testchannel")

        # 3. ЗАПУСК
        await parser.parse_posts(
            channel_entity=mock_channel_entity, channel_model=channel, limit=1
        )

        # 4. ПРОВЕРКИ
        post = await Post.objects.aget(
            telegram_message_id=data["telegram_message_id"]
        )

        assert post.text == current_text
        assert post.views == data["views"]

        expected_mentions = [
            m.replace("@", "").casefold() for m in data["mentions"]
        ]

        # То, что реально записалось в базу
        actual_mentions = post.mentions

        assert sorted(actual_mentions) == sorted(expected_mentions)

        # Проверка реакций
        reaction = await PostReaction.objects.aget(
            post=post, emoji=reaction_data["emoji"]
        )
        assert reaction.count == reaction_data["count"]

    @pytest.mark.asyncio
    async def test_parse_posts_media_and_pinned(
        self, channel, mock_client, parser
    ):
        """
        Тест на:
        1. Корректное определение media_type (на примере Photo).
        2. Корректное определение is_pinned на основе pinned_messages канала.
        """

        # 1. ПОДГОТОВКА ДАННЫХ
        message_id = 999
        pinned_id = 999

        channel.pinned_messages = [pinned_id]
        await channel.asave()

        mock_message = MagicMock()
        mock_message.id = message_id
        mock_message.service = False
        mock_message.text = "Media and pinned test"
        mock_message.date = datetime.now(timezone.utc)
        mock_message.views = 50
        mock_message.forwards = 5
        mock_message.replies = MagicMock(replies=2)
        mock_message.fwd_from = None
        mock_message.entities = []

        mock_message.media = MagicMock()
        mock_message.media.photo = MagicMock()

        mock_message.reactions = MagicMock(results=[])

        mock_client.get_messages.return_value = [mock_message]
        mock_channel_entity = MagicMock(username="testchannel")

        # 2. ЗАПУСК
        await parser.parse_posts(
            channel_entity=mock_channel_entity, channel_model=channel, limit=1
        )

        # 3. ПРОВЕРКИ
        post = await Post.objects.aget(telegram_message_id=message_id)

        assert post.media_type == "video"

        assert post.is_pinned is True

    @pytest.mark.asyncio
    async def test_parse_posts_non_pinned_no_media(
        self, channel, mock_client, parser
    ):
        """
        Тест на обычное сообщение без медиа и без закрепа.
        """
        mock_message = MagicMock()
        mock_message.id = 1000
        mock_message.service = False
        mock_message.text = "Plain text"
        mock_message.date = datetime.now(timezone.utc)
        mock_message.views = 0
        mock_message.forwards = 0
        mock_message.replies = MagicMock(replies=0)
        mock_message.fwd_from = None
        mock_message.entities = []
        mock_message.media = None
        mock_message.reactions = MagicMock(results=[])

        channel.pinned_messages = [1, 2, 3]
        await channel.asave()

        mock_client.get_messages.return_value = [mock_message]
        mock_channel_entity = MagicMock(username="testchannel")

        await parser.parse_posts(
            channel_entity=mock_channel_entity, channel_model=channel, limit=1
        )

        post = await Post.objects.aget(telegram_message_id=1000)

        assert post.media_type == "none"
        assert post.is_pinned is False

    @pytest.mark.asyncio
    async def test_parse_posts_complex_reactions(
        self, channel, mock_client, parser
    ):
        """
        Тест на:
        1. Стабильные ключи для CustomEmoji (c:<hash>) и Paid (paid).
        2. Суммирование реакций с одинаковым ключом.
        3. Обработку двух кастомных и одной платной реакции.
        """
        from telethon.tl.types import ReactionCustomEmoji, ReactionPaid

        # 1. ПОДГОТОВКА ДАННЫХ
        mock_message = MagicMock()
        mock_message.id = 777
        mock_message.service = False
        mock_message.text = "Complex reactions test"
        mock_message.date = datetime.now(timezone.utc)
        mock_message.views = 100
        mock_message.forwards = 0
        mock_message.replies = MagicMock(replies=0)
        mock_message.fwd_from = None
        mock_message.entities = []

        r1 = MagicMock()
        r1.reaction = ReactionCustomEmoji(document_id=101)
        r1.count = 5

        r2 = MagicMock()
        r2.reaction = ReactionCustomEmoji(document_id=101)
        r2.count = 3

        r3 = MagicMock()
        r3.reaction = ReactionCustomEmoji(document_id=202)
        r3.count = 10

        r4 = MagicMock()
        r4.reaction = ReactionPaid()
        r4.count = 2

        mock_reactions_container = MagicMock()
        mock_reactions_container.results = [r1, r2, r3, r4]
        mock_message.reactions = mock_reactions_container

        mock_client.get_messages.return_value = [mock_message]
        mock_channel_entity = MagicMock(username="testchannel")

        # 2. ЗАПУСК
        await parser.parse_posts(
            channel_entity=mock_channel_entity, channel_model=channel, limit=1
        )

        # 3. ПРОВЕРКИ
        post = await Post.objects.aget(telegram_message_id=777)
        reactions = [r async for r in PostReaction.objects.filter(post=post)]

        assert len(reactions) == 3

        summed_reaction = next(
            (
                r
                for r in reactions
                if r.emoji.startswith("c:") and len(r.emoji) == 10
            ),
            None,
        )
        assert summed_reaction is not None
        assert summed_reaction.count == 8

        other_custom = next(
            (r for r in reactions if r.emoji != summed_reaction.emoji), None
        )
        assert other_custom.emoji.startswith("c:")
        assert other_custom.count == 10

        # Проверка платной реакции
        paid_reaction = next((r for r in reactions if r.emoji == "paid"), None)
        assert paid_reaction is not None
        assert paid_reaction.count == 2
