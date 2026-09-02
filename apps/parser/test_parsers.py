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
    return await TelegramChannel.objects.acreate(
        channel_id=12345, title="Test Channel", username="testchannel"
    )


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
            mock_message.fwd_from = MagicMock(channel_id=data["fwd_from"])
        else:
            mock_message.fwd_from = None

        mock_message.entities = []

        reaction_data = load_fixture("post_reaction")[0]

        mock_reaction_item = MagicMock()
        mock_reaction_item.emoticon = reaction_data["emoji"]
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

        expected_mentions = [m.replace("@", "") for m in data["mentions"]]

        # То, что реально записалось в базу
        actual_mentions = post.mentions

        assert sorted(actual_mentions) == sorted(expected_mentions)

        # Проверка реакций
        reaction = await PostReaction.objects.aget(
            post=post, emoji=reaction_data["emoji"]
        )
        assert reaction.count == reaction_data["count"]
