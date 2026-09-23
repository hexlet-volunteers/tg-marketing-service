from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from pydantic import ValidationError

from apps.ai.exceptions import AIUnavailable
from apps.ai.parsing import (
    IdeasResponse,
    get_ai_response,
    parse_response,
    with_ai_fallback,
)


def idea_kwargs(**overrides):
    # Возвращает новый словарь при каждом вызове, а не общий объект.
    return {
        "channel_title": "Канал",
        "category": "tech",
        "channel_description": "описание канала",
        "last_messages_block": "1) Пост (100 просмотров)",
        "idea_count": 3,
        **overrides,
    }


def fallback_ideas_dict():
    return {
        "ideas": [
            {
                "title": "Эвристическая идея",
                "description": "Собрана без AI",
                "format": "текстовый пост",
            }
        ]
    }


# Валидный JSON-ответ LLM для темы "ideas"
VALID_IDEAS_JSON = (
    '{"ideas": [{"title": "t", "description": "d", "format": "опрос"}]}'
)


class ParseResponseTest(TestCase):
    def test_valid_json_parses_into_dto(self):
        result = parse_response("ideas", VALID_IDEAS_JSON)

        self.assertIsInstance(result, IdeasResponse)
        self.assertEqual(result.ideas[0].title, "t")
        self.assertEqual(result.ideas[0].description, "d")
        self.assertEqual(result.ideas[0].format, "опрос")

    def test_json_wrapped_in_markdown_fence_is_normalized(self):
        raw = f"```json\n{VALID_IDEAS_JSON}\n```"

        result = parse_response("ideas", raw)

        self.assertIsInstance(result, IdeasResponse)
        self.assertEqual(result.ideas[0].title, "t")

    def test_json_wrapped_in_plain_fence_is_normalized(self):
        raw = f"```\n{VALID_IDEAS_JSON}\n```"

        result = parse_response("ideas", raw)

        self.assertIsInstance(result, IdeasResponse)

    def test_invalid_json_is_rejected(self):
        with self.assertRaises(AIUnavailable) as ctx:
            parse_response("ideas", "это не json {{{")

        self.assertIn("невалидный JSON", str(ctx.exception))

    def test_json_missing_required_field_is_rejected(self):
        raw = '{"ideas": [{"title": "t"}]}'

        with self.assertRaises(AIUnavailable) as ctx:
            parse_response("ideas", raw)

        self.assertIn("не подходит под схему", str(ctx.exception))

    def test_unknown_insight_type_is_rejected(self):
        raw = '{"insights": [{"type": "unknown_type", "text": "x"}]}'

        with self.assertRaises(AIUnavailable) as ctx:
            parse_response("insights", raw)

        self.assertIn("не подходит под схему", str(ctx.exception))

    def test_unknown_topic_is_rejected(self):
        with self.assertRaises(AIUnavailable) as ctx:
            parse_response("no-such-topic", "{}")

        self.assertIn("Нет схемы ответа для темы", str(ctx.exception))


@override_settings(
    AI_ENABLED=True,
    AI_API_KEY="test-key",
    AI_MODEL="claude-sonnet-5",
    AI_TIMEOUT_SECONDS=30,
    AI_MAX_TOKENS=1024,
)
class GetAiResponseTest(TestCase):
    @patch("apps.ai.parsing.generate")
    def test_builds_prompt_and_parses_valid_response(self, mock_generate):
        mock_generate.return_value = VALID_IDEAS_JSON

        result = get_ai_response("ideas", **idea_kwargs())

        self.assertIsInstance(result, IdeasResponse)
        self.assertEqual(result.ideas[0].title, "t")
        mock_generate.assert_called_once()
        _, kwargs = mock_generate.call_args
        self.assertIn("<channel>", kwargs["prompt"])
        self.assertIn("Канал", kwargs["prompt"])

    @patch("apps.ai.parsing.generate")
    def test_invalid_llm_response_raises(self, mock_generate):
        mock_generate.return_value = "не json"

        with self.assertRaises(AIUnavailable):
            get_ai_response("ideas", **idea_kwargs())


@override_settings(AI_ENABLED=True, AI_API_KEY="test-key")
class WithAiFallbackTest(TestCase):
    @override_settings(AI_ENABLED=False)
    @patch("apps.ai.client.Anthropic")
    def test_fallback_used_when_ai_disabled(self, mock_anthropic_cls):
        result = with_ai_fallback("ideas", fallback_ideas_dict, **idea_kwargs())

        # generate() здесь настоящий (не замокан) - AI_ENABLED=False
        # должен остановить его раньше, чем он дойдёт до Anthropic SDK.
        # Если бы этот код был сломан и всё равно пытался обратиться
        # к Anthropic, тест сразу бы это показал.
        mock_anthropic_cls.assert_not_called()
        self.assertIsInstance(result, IdeasResponse)
        self.assertEqual(result.ideas[0].title, "Эвристическая идея")

    @patch("apps.ai.parsing.generate")
    def test_fallback_used_when_client_raises(self, mock_generate):
        mock_generate.side_effect = AIUnavailable("нет ключа")

        result = with_ai_fallback("ideas", fallback_ideas_dict, **idea_kwargs())

        self.assertIsInstance(result, IdeasResponse)

    @patch("apps.ai.parsing.generate")
    def test_successful_ai_response_is_returned_without_fallback(
        self, mock_generate
    ):
        mock_generate.return_value = VALID_IDEAS_JSON
        fallback = Mock(side_effect=fallback_ideas_dict)

        result = with_ai_fallback("ideas", fallback, **idea_kwargs())

        self.assertIsInstance(result, IdeasResponse)
        self.assertEqual(result.ideas[0].title, "t")
        fallback.assert_not_called()

    @patch("apps.ai.parsing.generate")
    def test_fallback_result_is_same_dto_type_as_ai_response(
        self, mock_generate
    ):
        # fallback может вернуть готовый объект DTO вместо dict - тоже ок.
        mock_generate.side_effect = AIUnavailable("нет ключа")
        fallback_dto = IdeasResponse.model_validate(fallback_ideas_dict())

        result = with_ai_fallback(
            "ideas", lambda: fallback_dto, **idea_kwargs()
        )

        self.assertIsInstance(result, IdeasResponse)
        self.assertIs(result, fallback_dto)

    @patch("apps.ai.parsing.generate")
    def test_fallback_returning_wrong_shape_raises(self, mock_generate):
        # fallback вернул что-то, что не подходит под схему IdeasResponse -
        # это баг в самой fallback-функции, и он не должен прятаться.
        mock_generate.side_effect = AIUnavailable("нет ключа")

        with self.assertRaises(ValidationError):
            with_ai_fallback(
                "ideas", lambda: "fallback-result", **idea_kwargs()
            )

    def test_bug_in_our_own_code_is_not_hidden_by_fallback(self):
        # Не хватает обязательных переменных для render() - это наш баг,
        # а не проблема AI, поэтому fallback не должен его прятать.
        with self.assertRaises(ValueError):
            with_ai_fallback("ideas", fallback_ideas_dict)

    @patch("apps.ai.parsing.generate")
    def test_exception_from_fallback_propagates(self, mock_generate):
        mock_generate.side_effect = AIUnavailable("AI упал")
        failing_fallback = Mock(side_effect=RuntimeError("БД тоже упала"))

        with self.assertRaises(RuntimeError):
            with_ai_fallback("ideas", failing_fallback, **idea_kwargs())
