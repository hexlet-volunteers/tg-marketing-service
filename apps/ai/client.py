from anthropic import Anthropic
from django.conf import settings

from apps.ai.exceptions import AIUnavailable


def generate(
    prompt: str,
    system: str | None = None,
    max_tokens: int | None = None
) -> str:
    """
    Генерирует ответ от LLM. При недоступности AI бросает AIUnavailable.

    Аргументы:
    - prompt: конкретный запрос пользователя
    - system: инструкция для модели - роль, формат ответа, правила
    - max_tokens: максимальное количество токенов для конкретного вызова
    """
    actual_max_tokens = (
        settings.AI_MAX_TOKENS
        if max_tokens is None
        else max_tokens
    )
    if not settings.AI_ENABLED:
        raise AIUnavailable("AI is disabled")

    if not settings.AI_API_KEY:
        raise AIUnavailable("missing AI API key")

    try:
        client = Anthropic(
            api_key=settings.AI_API_KEY,
            timeout=settings.AI_TIMEOUT_SECONDS,
            max_retries=2
        )
        response = client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=actual_max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}]  
        )
        return response.content[0].text
    except Exception as e:
        raise AIUnavailable(f"Provider error: {e}") from e