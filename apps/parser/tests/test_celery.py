from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone

import apps.parser.tasks as tasks
from apps.parser.models import Post, PostAnalysis, TelegramChannel
from apps.parser.services.analysis import PostAnalysisService


class ParserRegressionTests(TestCase):
    def setUp(self):
        self.channel = TelegramChannel.objects.create(
            channel_id=1, username="test_channel", title="Test Channel"
        )
        self.post = Post.objects.create(
            channel=self.channel,
            telegram_message_id=123,
            text="Test post content",
            published_at=timezone.now(),
            views=100,
            forwards=10,
            comments_count=5,
        )

    def test_trigger_analysis_uses_celery_delay(self):
        """
        Проверка, что при необходимости анализа вызывается .delay().
        Используем patch.object на импортированный модуль задач.
        """
        with patch.object(tasks.run_post_analysis_task, "delay") as mock_delay:
            with patch("django.core.cache.cache.get", return_value=None):
                PostAnalysisService.trigger_analysis_if_needed(self.post)

            mock_delay.assert_called_once_with(self.post.id)

    def test_analysis_is_regenerated_after_ttl_expires(self):
        """
        Проверка, что если анализ старый, он перегенерируется.
        """
        old_date = timezone.now() - timedelta(days=10)
        PostAnalysis.objects.create(
            post=self.post,
            why_worked="Old analysis",
            how_to_improve="Old improvement",
            generated_at=old_date,
        )

        mock_provider = MagicMock()
        mock_provider.analyze.return_value = {
            "why_worked": ["New why"],
            "how_to_improve": ["New improvement"],
            "similar_posts_ids": [],
        }
        mock_provider.__class__.__name__ = "MockProvider"

        service = PostAnalysisService(provider=mock_provider)

        new_analysis = service.get_analysis(self.post, force_regenerate=True)

        self.assertEqual(new_analysis.why_worked, "New why")

        updated_analysis = PostAnalysis.objects.get(post=self.post)
        self.assertEqual(updated_analysis.why_worked, "New why")

        mock_provider.analyze.assert_called_once()

    def test_analysis_is_considered_fresh_within_ttl(self):
        """
        Проверка, что свежий анализ не перегенерируется.
        """
        existing_analysis = PostAnalysis.objects.create(
            post=self.post,
            why_worked="Fresh analysis",
            how_to_improve="Fresh improvement",
            generated_at=timezone.now(),
        )

        mock_provider = MagicMock()
        service = PostAnalysisService(provider=mock_provider)

        result = service.get_analysis(self.post)

        self.assertEqual(result.id, existing_analysis.id)
        self.assertEqual(result.why_worked, "Fresh analysis")
        mock_provider.analyze.assert_not_called()
