from types import SimpleNamespace
from unittest.mock import patch

from anthropic import APITimeoutError
from django.test import TestCase, override_settings

from apps.ai.client import generate
from apps.ai.exceptions import AIUnavailable


@override_settings(
    AI_ENABLED=True,
    AI_API_KEY="test-key",
    AI_MODEL="claude-sonnet-5",
    AI_TIMEOUT_SECONDS=30,
    AI_MAX_TOKENS=1024,
)
class AIClientTest(TestCase):
    @patch("apps.ai.client.Anthropic")
    def test_generate_success(self, mock_anthropic_cls):
        mock_client = mock_anthropic_cls.return_value
        mock_client.messages.create.return_value.content = [
            SimpleNamespace(text="Ответ модели")
        ]

        result = generate(
            prompt="Проанализируй пост",
            system="Ты аналитик",
            max_tokens=256,
        )

        self.assertEqual(result, "Ответ модели")
        mock_client.messages.create.assert_called_once_with(
            model="claude-sonnet-5",
            max_tokens=256,
            system="Ты аналитик",
            messages=[{"role": "user", "content": "Проанализируй пост"}],
        )
    
    @patch("apps.ai.client.Anthropic")
    def test_generate_default_max_tokens(self, mock_anthropic_cls):
        mock_client = mock_anthropic_cls.return_value
        mock_client.messages.create.return_value.content = [
            SimpleNamespace(text="Ответ модели")
        ]

        result = generate(
            prompt="тест",
            system="Ты аналитик",
        )

        self.assertEqual(result, "Ответ модели")
        mock_client.messages.create.assert_called_once_with(
            model="claude-sonnet-5",
            max_tokens=1024,
            system="Ты аналитик",
            messages=[{"role": "user", "content": "тест"}],
        )

    @patch("apps.ai.client.Anthropic")
    def test_generate_without_system_and_max_tokens(self, mock_anthropic_cls):
        mock_client = mock_anthropic_cls.return_value
        mock_client.messages.create.return_value.content = [
            SimpleNamespace(text="Ответ модели")
        ]

        result = generate(prompt="тест")

        self.assertEqual(result, "Ответ модели")
        mock_client.messages.create.assert_called_once_with(
            model="claude-sonnet-5",
            max_tokens=1024,
            system="",
            messages=[{"role": "user", "content": "тест"}],
        )
    
    @override_settings(AI_ENABLED=True, AI_API_KEY=None)
    @patch("apps.ai.client.Anthropic")
    def test_generate_missing_api_key(self, mock_anthropic_cls):
        with self.assertRaises(AIUnavailable):
            generate("тест")
        mock_anthropic_cls.assert_not_called()

    @override_settings(AI_ENABLED=False)
    @patch("apps.ai.client.Anthropic")
    def test_generate_ai_disabled(self, mock_anthropic_cls):
        with self.assertRaises(AIUnavailable):
            generate("тест")
        mock_anthropic_cls.assert_not_called()

    @override_settings(AI_ENABLED=True, AI_API_KEY="test-key")
    @patch("apps.ai.client.Anthropic")
    def test_generate_provider_error(self, mock_anthropic_cls):
        mock_client = mock_anthropic_cls.return_value
        mock_client.messages.create.side_effect = Exception("boom")

        with self.assertRaises(AIUnavailable) as ctx:
            generate("тест")

        self.assertIn("Provider error", str(ctx.exception))
        mock_client.messages.create.assert_called_once_with(
            model="claude-sonnet-5",
            max_tokens=1024,
            system="",
            messages=[{"role": "user", "content": "тест"}],
        )

    @patch("apps.ai.client.Anthropic")
    def test_generate_timeout_error(self, mock_anthropic_cls):
        mock_client = mock_anthropic_cls.return_value
        mock_client.messages.create.side_effect = APITimeoutError(
            "Request timed out"
            )

        with self.assertRaises(AIUnavailable) as ctx:
            generate(prompt="тест")

        self.assertIn("Provider error", str(ctx.exception))
        mock_client.messages.create.assert_called_once_with(
            model="claude-sonnet-5",
            max_tokens=1024,
            system="",
            messages=[{"role": "user", "content": "тест"}],
        )