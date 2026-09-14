import json
import logging
from typing import Any, Callable, Literal

from pydantic import BaseModel, ValidationError

from apps.ai.client import generate
from apps.ai.exceptions import AIUnavailable
from apps.ai.prompts import get_prompt

log = logging.getLogger(__name__)


class IdeaItem(BaseModel):
    title: str
    description: str
    format: str


class IdeasResponse(BaseModel):
    ideas: list[IdeaItem]


class TimeRecommendation(BaseModel):
    day_of_week: str
    time_range: str
    reasoning: str


class BestTimeResponse(BaseModel):
    recommendations: list[TimeRecommendation]
    confidence: str
    limitations: str


class InsightItem(BaseModel):
    type: Literal["trend", "recommendation", "warning", "positive"]
    text: str


class InsightsResponse(BaseModel):
    insights: list[InsightItem]


class PostAnalysisResponse(BaseModel):
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]


class AskResponse(BaseModel):
    answer: str


class CompareDifference(BaseModel):
    metric: str
    channel_a: str
    channel_b: str
    comment: str


class CompareResponse(BaseModel):
    summary: str
    differences: list[CompareDifference]


class CompetitorGap(BaseModel):
    area: str
    delta_description: str
    recommendation: str


class CompetitorDeltaResponse(BaseModel):
    summary: str
    gaps: list[CompetitorGap]


class ComposerVariant(BaseModel):
    text: str
    tone: str


class ComposerResponse(BaseModel):
    variants: list[ComposerVariant]


RESPONSE_MODELS: dict[str, type[BaseModel]] = {
    "ideas": IdeasResponse,
    "best-time": BestTimeResponse,
    "insights": InsightsResponse,
    "post-analysis": PostAnalysisResponse,
    "ask": AskResponse,
    "compare": CompareResponse,
    "competitor-delta": CompetitorDeltaResponse,
    "composer": ComposerResponse,
}


def _normalize_raw_json(raw_text: str) -> str:
    """
    Приводит сырой ответ LLM к виду, который можно передать в json.loads.
    """
    text = raw_text.strip()
    if not text.startswith("```"):
        return text

    first_line_end = text.find("\n")
    if first_line_end == -1:
        return text

    text = text[first_line_end + 1 :]
    if text.endswith("```"):
        text = text[: -len("```")]
    return text.strip()


def parse_response(topic: str, raw_text: str) -> BaseModel:
    """
    Превращает текстовый ответ LLM в pydantic-объект нужной темы.

    Аргументы:
        topic (str): тема промпта, например "ideas" (ключ в RESPONSE_MODELS)
        raw_text (str): сырой текстовый ответ, который вернул generate()
    """
    model_cls = RESPONSE_MODELS.get(topic)
    if model_cls is None:
        raise AIUnavailable(f"Нет схемы ответа для темы {topic!r}")

    try:
        data = json.loads(_normalize_raw_json(raw_text))
    except json.JSONDecodeError as error:
        raise AIUnavailable(
            f"LLM вернул невалидный JSON для темы {topic!r}: {error}"
        ) from error

    try:
        return model_cls.model_validate(data)
    except ValidationError as error:
        raise AIUnavailable(
            f"Ответ LLM не подходит под схему темы {topic!r}: {error}"
        ) from error


def get_ai_response(topic: str, **prompt_vars: Any) -> BaseModel:
    """
    Собирает промпт по теме, отправляет его в LLM и парсит ответ в DTO.

    Аргументы:
        topic (str): тема промпта, например "ideas"
        **prompt_vars: переменные для шаблона темы
    """
    template = get_prompt(topic)
    prompt_text = template.render(**prompt_vars)
    raw_answer = generate(prompt=prompt_text, system=template.system)
    return parse_response(topic, raw_answer)


def with_ai_fallback(
    topic: str,
    fallback_factory: Callable[[], Any],
    **prompt_vars: Any,
) -> Any:
    """
    Пытается получить ответ от AI по теме `topic`.

    Если AI выключен, недоступен или вернул кривой ответ - не роняет
    вызывающий код исключением, а тихо возвращает fallback_factory().
    Так фича на странице продолжит показывать хоть что-то вместо
    сломанного дашборда.

    Аргументы:
        topic (str): тема промпта, например "ideas"
        fallback_factory: функция без аргументов, которую пишет вызывающий
            код (например, эвристика "топ постов по просмотрам");
            parsing.py ничего не знает о бизнес-логике конкретной фичи
        **prompt_vars: переменные для шаблона темы
    """
    try:
        return get_ai_response(topic, **prompt_vars)
    except AIUnavailable as error:
        log.warning("AI fallback сработал для темы %r: %s", topic, error)
        fallback_result = fallback_factory()
        return _ensure_response_type(topic, fallback_result)


def _ensure_response_type(topic: str, value: Any) -> BaseModel:
    """
    Проверяет, что fallback_factory вернул тот же DTO, что и AI-ответ
    для этой темы, чтобы код фичи всегда получал один и тот же тип
    независимо от того, ответил AI или сработал fallback.
    """
    model_cls = RESPONSE_MODELS[topic]
    return model_cls.model_validate(value)
