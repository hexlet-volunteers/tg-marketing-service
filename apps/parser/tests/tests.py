from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time  # type: ignore

from apps.parser.models import Post, PostAnalysis, TelegramChannel
from apps.parser.services.analysis import PostAnalysisService


@override_settings(SECRET_KEY="test-key-for-testing")
class PostAIAnalysisAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.channel = TelegramChannel.objects.create(
            channel_id=123456, title="Test Channel", username="test"
        )
        self.post = Post.objects.create(
            channel=self.channel,
            telegram_message_id=12345,
            text="Original post text",
            published_at=timezone.now(),
        )

    def test_endpoint_404_if_post_not_found(self):
        url = reverse(
            "parser:post_ai_analysis",
            kwargs={"channel_id": self.channel.id, "post_id": 99999},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch("apps.parser.services.analysis.PostAnalysisService.get_analysis")
    def test_endpoint_cache_hit(self, mock_get_analysis):
        analysis = PostAnalysis.objects.create(
            post=self.post,
            why_worked="Reason 1\nReason 2",
            how_to_improve="Improve 1",
        )
        mock_get_analysis.return_value = analysis

        url = reverse(
            "parser:post_ai_analysis",
            kwargs={"channel_id": self.channel.id, "post_id": 12345},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["why_worked"], ["Reason 1", "Reason 2"]
        )

    def test_endpoint_cache_miss_and_llm_call(self):
        """Проверка: нет анализа -> вызываем LLM -> сохраняем"""
        mock_provider = MagicMock()
        mock_provider.analyze.return_value = {
            "why_worked": ["AI Reason"],
            "how_to_improve": ["AI Improvement"],
            "similar_posts_ids": [],
        }

        service = PostAnalysisService(provider=mock_provider)

        # Патчим создание сервиса внутри view, чтобы подставить наш мок
        with patch(
            "apps.parser.views.PostAnalysisService", return_value=service
        ):
            url = reverse(
                "parser:post_ai_analysis",
                kwargs={"channel_id": self.channel.id, "post_id": 12345},
            )

            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["why_worked"], ["AI Reason"])

            # Проверка, что при втором запросе провайдер НЕ вызывается
            self.client.get(url)
            self.assertEqual(mock_provider.analyze.call_count, 1)

    @freeze_time("2024-01-01 12:00:00")
    def test_endpoint_regenerates_after_ttl_expired(self):
        """
        Если анализ старый, сервис должен вызвать провайдера снова.
        """
        # 1. Создаем "старый" анализ (например, 10 дней назад)
        old_date = timezone.now() - timedelta(days=10)
        analysis = PostAnalysis.objects.create(
            post=self.post,
            why_worked="Old Reason",
            how_to_improve="Old Improvement",
        )
        # Вручную подменяем дату создания
        analysis.created_at = old_date
        analysis.save()

        # 2. Настраиваем мок провайдера на возврат НОВЫХ данных
        mock_provider = MagicMock()
        mock_provider.analyze.return_value = {
            "why_worked": ["New Reason"],
            "how_to_improve": ["New Improvement"],
            "similar_posts_ids": [],
        }
        service = PostAnalysisService(provider=mock_provider)

        # 3. Патчим сервис во вьюхе
        with patch(
            "apps.parser.views.PostAnalysisService", return_value=service
        ):
            url = reverse(
                "parser:post_ai_analysis",
                kwargs={"channel_id": self.channel.id, "post_id": 12345},
            )

            # 4. Выполняем запрос
            response = self.client.get(url)

            # 5. ПРОВЕРКИ
            self.assertEqual(response.status_code, 200)
            # Данные должны быть НОВЫМИ, а не "Old Reason"
            self.assertEqual(response.json()["why_worked"], ["New Reason"])
            # Провайдер ДОЛЖЕН был быть вызван, несмотря на наличие записи в БД
            self.assertEqual(mock_provider.analyze.call_count, 1)
