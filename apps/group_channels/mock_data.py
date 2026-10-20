"""Мок-реестр данных страниц подборок (Inertia: Collections, Collection).

Каталог (/collections/) и детальная страница (/collections/<pk>/) отдают
данные отсюда до подключения БД. Данные перенесены сюда из
frontend/src/shared/mocks/collections, chCollection и
frontend/src/utils/addColors (цвета каналов).
"""

from collections import defaultdict
from typing import Any, Dict, List

from apps.group_channels.dto.collections_dto import (
    CollectionDTO,
    CollectionsCatalogDTO,
    CollectionSectionDTO,
    CollectionsFiltersDTO,
)

MOCK_COLLECTION_TITLE = "Топ IT-каналов"
MOCK_COLLECTION_DESCRIPTION = "Технологии, разработка и цифровые продукты"

COLLECTION_CHANNEL_COLORS = [
    "var(--mantine-color-tgblue-5)",
    "var(--mantine-color-tgpurple-5)",
    "var(--mantine-color-tgblue-4)",
]

MOCK_COLLECTION_CHANNELS: List[Dict[str, Any]] = [
    {
        "name": "Product Radar",
        "username": "@product_radar",
        "subscribers": 142000,
        "er": 26.9,
        "growth30d": 2480,
    },
    {
        "name": "Тренды AI",
        "username": "@ai_trends",
        "subscribers": 98345,
        "er": 29.5,
        "growth30d": 4300,
    },
    {
        "name": "Код на ночь",
        "username": "@night_code",
        "subscribers": 47850,
        "er": 33.2,
        "growth30d": 610,
    },
]


def build_mock_collection_channels() -> List[Dict[str, Any]]:
    """Возвращает каналы подборки с ротацией цветов."""
    return [
        {
            **channel,
            "color": COLLECTION_CHANNEL_COLORS[
                index % len(COLLECTION_CHANNEL_COLORS)
            ],
        }
        for index, channel in enumerate(MOCK_COLLECTION_CHANNELS)
    ]


# Мок-реестр каталога подборок. Поля соответствуют CollectionDTO
# (id, name, slug, description, is_editorial, curator, channel_count,
# cover, gradient_key); country/category — только для фильтрации.
MOCK_COLLECTIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Топ IT-каналов",
        "slug": "top-it",
        "description": "Технологии, разработка и цифровые продукты",
        "is_editorial": True,
        "curator": "Редакция tgpulse",
        "channel_count": 3,
        "cover": "",
        "gradient_key": "collection-1",
        "country": "Россия",
        "category": "Технологии",
    },
    {
        "id": 2,
        "name": "Маркетинг и SMM",
        "slug": "marketing-smm",
        "description": "Продвижение, реклама и контент",
        "is_editorial": True,
        "curator": "Редакция tgpulse",
        "channel_count": 1,
        "cover": "",
        "gradient_key": "collection-2",
        "country": "Россия",
        "category": "Маркетинг",
    },
    {
        "id": 3,
        "name": "Крипта без шума",
        "slug": "crypto-calm",
        "description": "Аналитика рынка без хайпа",
        "is_editorial": False,
        "curator": "@crypta_daily",
        "channel_count": 1,
        "cover": "",
        "gradient_key": "collection-3",
        "country": "Казахстан",
        "category": "Криптовалюты",
    },
    {
        "id": 4,
        "name": "Стартапы и венчур",
        "slug": "startups-venture",
        "description": "Истории, разборы и деньги",
        "is_editorial": True,
        "curator": "Редакция tgpulse",
        "channel_count": 2,
        "cover": "",
        "gradient_key": "collection-4",
        "country": "Россия",
        "category": "Бизнес",
    },
    {
        "id": 5,
        "name": "Дизайн и продукт",
        "slug": "design-product",
        "description": "UX, UI и продуктовое мышление",
        "is_editorial": False,
        "curator": "@design_kitchen",
        "channel_count": 2,
        "cover": "",
        "gradient_key": "collection-5",
        "country": "Россия",
        "category": "Дизайн",
    },
    {
        "id": 6,
        "name": "Финансы и инвестиции",
        "slug": "finance-invest",
        "description": "Личные финансы и рынки",
        "is_editorial": True,
        "curator": "Редакция tgpulse",
        "channel_count": 2,
        "cover": "",
        "gradient_key": "collection-6",
        "country": "Россия",
        "category": "Финансы",
    },
]

_MOCK_COLLECTION_DTO_FIELDS = (
    "id",
    "name",
    "slug",
    "description",
    "is_editorial",
    "curator",
    "channel_count",
    "cover",
    "gradient_key",
)


def _mock_collection_dto(data: Dict[str, Any]) -> CollectionDTO:
    return CollectionDTO.model_validate(
        {field: data[field] for field in _MOCK_COLLECTION_DTO_FIELDS}
    )


def build_mock_catalog(
    q: str | None = None,
    country: str | None = None,
    category: str | None = None,
) -> CollectionsCatalogDTO:
    """Собирает мок-каталог подборок с учётом фильтров."""
    items = MOCK_COLLECTIONS

    if q:
        needle = q.lower()
        items = [
            item
            for item in items
            if needle in item["name"].lower()
            or needle in item["description"].lower()
        ]

    if country:
        items = [item for item in items if item["country"] == country]

    if category:
        items = [item for item in items if item["category"] == category]

    collections = [_mock_collection_dto(item) for item in items]

    featured = [
        _mock_collection_dto(item)
        for item in sorted(
            items,
            key=lambda item: (
                not item["is_editorial"],
                item["id"],
            ),
        )[:3]
    ]

    sections: Dict[str, List[CollectionDTO]] = defaultdict(list)

    for item in items:
        sections[item["category"]].append(_mock_collection_dto(item))

    section_dtos = [
        CollectionSectionDTO(
            title=title,
            collections=section_collections,
            count=len(section_collections),
        )
        for title, section_collections in sorted(sections.items())
    ]

    country_options = sorted({item["country"] for item in MOCK_COLLECTIONS})
    category_options = sorted({item["category"] for item in MOCK_COLLECTIONS})

    return CollectionsCatalogDTO(
        featured=featured,
        collections=collections,
        sections=section_dtos,
        filters=CollectionsFiltersDTO(
            q=q,
            country=country,
            category=category,
            country_options=country_options,
            category_options=category_options,
        ),
    )

