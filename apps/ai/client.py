from anthropic import Anthropic, APIError
from django.conf import settings

from apps.ai.exceptions import AIUnavailable


def generate(
    prompt: str, system: str | None = None, max_tokens: int | None = None
) -> str:
    """
    Генерирует ответ от LLM. При недоступности AI бросает AIUnavailable.

    Аргументы:
    - prompt: конкретный запрос пользователя
    - system: инструкция для модели - роль, формат ответа, правила
    - max_tokens: максимальное количество токенов для конкретного вызова
    """
    actual_max_tokens = (
        settings.AI_MAX_TOKENS if max_tokens is None else max_tokens
    )
    if not settings.AI_ENABLED:
        raise AIUnavailable("AI is disabled")
    if not settings.AI_API_KEY:
        raise AIUnavailable("missing AI API key")

    try:
        client = Anthropic(
            api_key=settings.AI_API_KEY,
            timeout=settings.AI_TIMEOUT_SECONDS,
            max_retries=2,
        )
        response = client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=actual_max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
    except APIError as e:
        raise AIUnavailable(f"Anthropic error: {e}") from e

    if not response.content:
        raise AIUnavailable("Invalid provider response: empty content")

    for block in response.content:
        if block.type == "text" and block.text:
            return block.text

    raise AIUnavailable("Invalid response: no text block found")
