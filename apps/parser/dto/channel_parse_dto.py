"""DTO формы добавления канала (Inertia: ``Parser``).

Контракт зафиксирован в ``docs/inertia-contract.md``, сборка props —
``apps/parser/services/channel_parse.py``.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class FormErrorDTO(BaseModel):
    """Ошибка валидации одного поля формы."""

    message: str
    code: str = ""


class ParserFormDTO(BaseModel):
    """Состояние формы: значения полей и ошибки валидации.

    Формат ошибок общий для форм проекта:
    ``{"<field>": [{"message": "...", "code": "..."}]}``.
    """

    data: Dict[str, Any] = Field(default_factory=dict)
    errors: Dict[str, List[FormErrorDTO]] = Field(default_factory=dict)


class ParserOptionsDTO(BaseModel):
    """Справочники формы: категории и границы количества постов."""

    categories: List[str] = Field(default_factory=list)
    limit_min: int = 1
    limit_max: int = 20
    limit_initial: int = 10


class ParserPropsDTO(BaseModel):
    """Props страницы ``Parser`` (``GET /parser/``)."""

    form: ParserFormDTO
    options: ParserOptionsDTO
