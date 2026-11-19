# tests/test_post_metrics.py
import datetime

from django.test import TestCase
from django.utils import timezone

from apps.parser.models import Post, PostReaction, TelegramChannel
from apps.parser.services.metrics import posting_heatmap, reactions_breakdown


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


class PostingHeatmapTest(TestCase):
    def setUp(self):
        self.channel = TelegramChannel.objects.create(
            channel_id=123,
            title="Heatmap Test Channel",
            username="heatmap_test",
        )

    def test_heatmap_full_structure(self):
        result = posting_heatmap(self.channel)
        self.assertEqual(len(result), 84)
        self.assertEqual(
            result[0],
            {"weekday": 1, "hour": 9, "avg_reach": 0.0, "post_count": 0},
        )
        self.assertEqual(
            result[-1],
            {"weekday": 7, "hour": 20, "avg_reach": 0.0, "post_count": 0},
        )

    def test_heatmap_correct_calculations(self):
        """
        Проверка корректности расчетов
        """

        monday_date = timezone.make_aware(
            datetime.datetime(2024, 1, 1, 12, 0), datetime.timezone.utc
        )
        Post.objects.create(
            channel=self.channel,
            views=100,
            published_at=monday_date,
            telegram_message_id=101,
        )
        Post.objects.create(
            channel=self.channel,
            views=200,
            published_at=monday_date,
            telegram_message_id=102,
        )

        wednesday_date = timezone.make_aware(
            datetime.datetime(2024, 1, 3, 15, 0), datetime.timezone.utc
        )
        Post.objects.create(
            channel=self.channel,
            views=500,
            published_at=wednesday_date,
            telegram_message_id=103,
        )

        result = posting_heatmap(self.channel)

        # Проверяем Понедельник (weekday 1)
        monday_cell = next(
            (
                item
                for item in result
                if item["weekday"] == 1 and item["hour"] == 12
            ),
            None,
        )
        self.assertIsNotNone(
            monday_cell, "Ячейка для Понедельника (1) не найдена"
        )
        self.assertEqual(monday_cell["avg_reach"], 150.0)
        self.assertEqual(monday_cell["post_count"], 2)

        # Проверяем Среду (weekday 3)
        wednesday_cell = next(
            (
                item
                for item in result
                if item["weekday"] == 3 and item["hour"] == 15
            ),
            None,
        )
        self.assertIsNotNone(wednesday_cell, "Ячейка для Среды (3) не найдена")
        self.assertEqual(wednesday_cell["avg_reach"], 500.0)
        self.assertEqual(wednesday_cell["post_count"], 1)

    def test_heatmap_excludes_out_of_range_hours(self):
        utc = datetime.timezone.utc
        early_date = datetime.datetime(2026, 1, 1, 8, 0, tzinfo=utc)
        Post.objects.create(
            channel=self.channel,
            views=1000,
            published_at=early_date,
            telegram_message_id=201,
        )

        late_date = datetime.datetime(2026, 1, 1, 21, 0, tzinfo=utc)
        Post.objects.create(
            channel=self.channel,
            views=1000,
            published_at=late_date,
            telegram_message_id=202,
        )

        result = posting_heatmap(self.channel)

        for cell in result:
            self.assertNotEqual(cell["avg_reach"], 1000.0)

    def test_heatmap_consistency_with_empty_data(self):
        utc = datetime.timezone.utc
        post_date = datetime.datetime(2026, 1, 1, 12, 0, tzinfo=utc)
        Post.objects.create(
            channel=self.channel,
            views=100,
            published_at=post_date,
            telegram_message_id=301,
        )

        result = posting_heatmap(self.channel)
        active_cells = [c for c in result if c["post_count"] > 0]
        self.assertEqual(len(active_cells), 1)
        empty_cells = [c for c in result if c["post_count"] == 0]
        self.assertEqual(len(empty_cells), 83)
