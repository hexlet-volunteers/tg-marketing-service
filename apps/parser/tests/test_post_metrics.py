# tests/test_post_metrics.py
from django.test import TestCase
from django.utils import timezone

from apps.parser.models import Post, PostReaction, TelegramChannel
from apps.parser.services.metrics import reactions_breakdown


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

    def test_metrics_reactions_breakdown_aggregation(self):
        """Проверка, что функция собирает реакции со ВСЕХ постов канала."""
        post1 = Post.objects.create(
            channel=self.channel,
            telegram_message_id=1,
            text="P1",
            published_at=timezone.now(),
        )
        post2 = Post.objects.create(
            channel=self.channel,
            telegram_message_id=2,
            text="P2",
            published_at=timezone.now(),
        )

        PostReaction.objects.create(post=post1, emoji="👍", count=10)
        PostReaction.objects.create(post=post2, emoji="👍", count=20)
        PostReaction.objects.create(post=post2, emoji="❤️", count=5)

        result = reactions_breakdown(self.channel)

        self.assertIn("details", result)
        self.assertIn("others_percent", result)

        details = result["details"]
        self.assertEqual(len(details), 2)
        self.assertEqual(details[0]["emoji"], "👍")
        self.assertEqual(details[0]["count"], 30)
        self.assertEqual(details[1]["emoji"], "❤️")
        self.assertEqual(details[1]["count"], 5)

    def test_metrics_reactions_breakdown_top_n_limit(self):
        """Проверка ограничения Top-N и наличия остатка."""
        post = Post.objects.create(
            channel=self.channel,
            telegram_message_id=5,
            text="P5",
            published_at=timezone.now(),
        )
        PostReaction.objects.create(post=post, emoji="👍", count=100)
        PostReaction.objects.create(post=post, emoji="❤️", count=50)
        PostReaction.objects.create(post=post, emoji="🔥", count=10)

        result = reactions_breakdown(self.channel, top_n=2)

        self.assertEqual(len(result["details"]), 2)
        self.assertEqual(result["details"][0]["emoji"], "👍")
        self.assertEqual(result["details"][1]["emoji"], "❤️")
        self.assertGreater(result["others_percent"], 0)

    def test_metrics_reactions_breakdown_empty_channel(self):
        """Проверка возврата структуры с пустыми данными."""
        Post.objects.create(
            channel=self.channel,
            telegram_message_id=6,
            text="Empty",
            published_at=timezone.now(),
        )
        result = reactions_breakdown(self.channel)
        self.assertEqual(result, {"details": [], "others_percent": 0.0})

    def test_metrics_reactions_breakdown_percent_sum(self):
        """Проверка, что сумма деталей и остатка всегда ~100%."""
        post = Post.objects.create(
            channel=self.channel,
            telegram_message_id=7,
            text="P7",
            published_at=timezone.now(),
        )
        PostReaction.objects.create(post=post, emoji="A", count=1)
        PostReaction.objects.create(post=post, emoji="B", count=1)
        PostReaction.objects.create(post=post, emoji="C", count=1)

        result = reactions_breakdown(self.channel, top_n=2)

        total_percent = (
            sum(r["percent"] for r in result["details"])
            + result["others_percent"]
        )
        self.assertAlmostEqual(total_percent, 100.0, places=1)
