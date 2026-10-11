# tests/test_post_metrics.py
from django.test import TestCase

from apps.parser.models import Post, PostReaction, TelegramChannel


class PostMetricsTest(TestCase):
    def setUp(self):
        self.channel = TelegramChannel.objects.create(
            channel_id=123, title="Test Channel", username="test"
        )

    def test_er_calculation_with_data(self):
        """Проверка корректности формулы ER."""
        post = Post.objects.create(
            channel=self.channel,
            telegram_message_id=1,
            text="Test",
            views=100,
            forwards=10,
            comments_count=10,
            published_at="2024-01-01T00:00:00Z",
        )
        # Добавляем 30 реакций (10 👍 + 20 ❤️)
        PostReaction.objects.create(post=post, emoji="👍", count=10)
        PostReaction.objects.create(post=post, emoji="❤️", count=20)

        self.assertEqual(post.calculate_er(), 0.5)

    def test_er_zero_views(self):
        """Проверка обработки нулевых просмотров"""
        post = Post.objects.create(
            channel=self.channel,
            telegram_message_id=2,
            text="No views",
            views=0,
            published_at="2024-01-01T00:00:00Z",
        )
        self.assertEqual(post.calculate_er(), 0.0)

    def test_reactions_breakdown_empty(self):
        """Проверка случая, когда реакций нет вообще."""
        post = Post.objects.create(
            channel=self.channel,
            telegram_message_id=3,
            text="No reactions",
            views=100,
            published_at="2024-01-01T00:00:00Z",
        )
        breakdown = post.get_reactions_breakdown()

        self.assertEqual(breakdown["total"], 0)
        self.assertEqual(breakdown["details"], [])

    def test_reactions_breakdown_sorting_and_percent(self):
        """Проверка сортировки по убыванию и точности процентов."""
        post = Post.objects.create(
            channel=self.channel,
            telegram_message_id=4,
            text="Sorted",
            views=100,
            published_at="2024-01-01T00:00:00Z",
        )
        PostReaction.objects.create(post=post, emoji="🔥", count=10)
        PostReaction.objects.create(post=post, emoji="👍", count=90)

        breakdown = post.get_reactions_breakdown()

        self.assertEqual(breakdown["details"][0]["emoji"], "👍")
        self.assertEqual(breakdown["details"][0]["percent"], 90.0)
        self.assertEqual(breakdown["details"][1]["emoji"], "🔥")
        self.assertEqual(breakdown["details"][1]["percent"], 10.0)
