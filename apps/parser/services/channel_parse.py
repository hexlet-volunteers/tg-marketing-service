"""Сборка props страницы добавления канала (Inertia: ``Parser``).

Контракт зафиксирован в ``docs/inertia-contract.md``.
"""

from typing import Any

from apps.parser.dto.channel_parse_dto import (
    FormErrorDTO,
    ParserFormDTO,
    ParserOptionsDTO,
    ParserPropsDTO,
)
from apps.parser.forms import (
    CATEGORY_CHOICES,
    POSTS_LIMIT_INITIAL,
    POSTS_LIMIT_MAX,
    POSTS_LIMIT_MIN,
    ChannelParseForm,
)


def _build_form_data(form: ChannelParseForm) -> dict[str, Any]:
    """Значения полей: initial на GET, эхо введённого на bound POST."""
    data: dict[str, Any] = {}
    for name, field in form.fields.items():
        if form.is_bound:
            value = form.data.get(name, "")
        else:
            value = field.initial
        data[name] = "" if value is None else value
    return data


def _build_form_errors(
    form: ChannelParseForm,
) -> dict[str, list[FormErrorDTO]]:
    """Ошибки валидации в формате ``{field: [{message, code}]}``."""
    if not form.is_bound:
        return {}

    return {
        name: [
            FormErrorDTO(
                message=str(item.get("message", "")),
                code=str(item.get("code", "")),
            )
            for item in items
        ]
        for name, items in form.errors.get_json_data().items()
    }


def _build_options() -> ParserOptionsDTO:
    """Справочники формы из общих констант ``forms.py``."""
    return ParserOptionsDTO(
        categories=[str(value) for value, _label in CATEGORY_CHOICES],
        limit_min=POSTS_LIMIT_MIN,
        limit_max=POSTS_LIMIT_MAX,
        limit_initial=POSTS_LIMIT_INITIAL,
    )


def build_parser_props(form: ChannelParseForm) -> ParserPropsDTO:
    """Собирает props страницы ``Parser`` из состояния формы."""
    return ParserPropsDTO(
        form=ParserFormDTO(
            data=_build_form_data(form),
            errors=_build_form_errors(form),
        ),
        options=_build_options(),
    )
