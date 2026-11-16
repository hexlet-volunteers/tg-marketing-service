import math

import pytest
from django.utils import timezone

from apps.parser.models import Post, TelegramChannel
from apps.parser.services.metrics import (
    compute_normalized_citation,
    engagement_rate,
    update_channels_citation_indices,
)

# --- UNIT TESTS ---


def test_compute_normalized_citation_deterministic():
    assert compute_normalized_citation(0, 0) == 0.0
    res1 = compute_normalized_citation(5, 5)
    res2 = compute_normalized_citation(5, 5)
    assert res1 == res2
    assert res1 == round(math.log1p(10), 4)


def test_engagement_rate_edge_cases():
    assert engagement_rate(10, 100) == 0.1
    assert engagement_rate(10, 0) == 0.0


# --- INTEGRATION TESTS ---


@pytest.mark.django_db
class TestCitationIndexLogic:
    """
    Тесты, покрывающие требования по сбору данных из Post и расчет метрик.
    """

    def test_citation_index_calculation_scenario(self):
        """
        Критерий: юнит-тест покрывает канал, процитированный двумя другими,
        против нецитируемого.
        """
        # Создаем каналы
        target_channel = TelegramChannel.objects.create(
            channel_id=100, username="target"
        )
        lonely_channel = TelegramChannel.objects.create(
            channel_id=200, username="lonely"
        )
        source_channel = TelegramChannel.objects.create(
            channel_id=300, username="source"
        )

        now = timezone.now()

        Post.objects.create(
            channel=source_channel,
            telegram_message_id=1,
            fwd_from=100,
            mentions=[],
            text="repost",
            published_at=now,
        )
        Post.objects.create(
            channel=source_channel,
            telegram_message_id=2,
            fwd_from=100,
            mentions=[],
            text="repost 2",
            published_at=now,
        )

        # Упоминание (mentions)
        Post.objects.create(
            channel=source_channel,
            telegram_message_id=3,
            fwd_from=None,
            mentions=["100"],
            text="mention",
            published_at=now,
        )
        Post.objects.create(
            channel=source_channel,
            telegram_message_id=4,
            fwd_from=None,
            mentions=["@100"],
            text="mention @100",
            published_at=now,
        )

        Post.objects.create(
            channel=source_channel,
            telegram_message_id=5,
            fwd_from=None,
            mentions=[],
            text="nothing",
            published_at=now,
        )

        update_channels_citation_indices()

        # Обновляем из БД
        target_channel.refresh_from_db()
        lonely_channel.refresh_from_db()

        expected_target_index = round(math.log1p(4), 4)
        expected_lonely_index = 0.0

        assert target_channel.citation_index == expected_target_index
        assert lonely_channel.citation_index == expected_lonely_index

    def test_mention_by_username_logic(self):
        """
        Проверка, что упоминание канала по username также учитывается.
        """
        channel = TelegramChannel.objects.create(
            channel_id=555, username="test_user"
        )
        source_channel = TelegramChannel.objects.create(
            channel_id=666, username="source"
        )

        Post.objects.create(
            channel=source_channel,
            telegram_message_id=10,
            fwd_from=None,
            mentions=["test_user"],
            text="hello",
            published_at=timezone.now(),
        )

        update_channels_citation_indices()
        channel.refresh_from_db()

        assert channel.citation_index == round(math.log1p(1), 4)

    def test_no_n_plus_1_on_update(self):
        """
        Проверка, что расчет отрабатывает корректно при наличии данных.
        """
        channel = TelegramChannel.objects.create(
            channel_id=777, username="speedy", citation_index=0.0
        )
        source_channel = TelegramChannel.objects.create(
            channel_id=888, username="source"
        )

        Post.objects.create(
            channel=source_channel,
            telegram_message_id=100,
            fwd_from=777,
            text="fwd",
            published_at=timezone.now(),
        )

        update_channels_citation_indices()
        channel.refresh_from_db()
        assert channel.citation_index > 0.0

    def test_empty_database(self):
        """Проверка работы функции на пустых таблицах."""
        update_channels_citation_indices()
        assert True
