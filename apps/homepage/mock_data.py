"""Мок-реестр данных дашборда и лендинга homepage-приложения.

Отдаётся из view до подключения данных БД (см. docs/inertia-contract.md).
Данные перенесены сюда из frontend/src/shared/mocks/ (channelKpis,
channelsCollection, posts, widgets).
"""

from typing import Any, Dict, List

MOCK_CHANNEL: Dict[str, Any] = {
    "id": 1,
    "name": "Tech News RU",
    "username": "@technewsru",
    "type": "channel",
    "subscribers": 125000,
    "category": "Технологии",
    "verified": True,
    "country": "Россия",
    "imageUrl": "",
    "er": 8.3,
    "growth30d": 3.2,
}

MOCK_KPIS: List[Dict[str, Any]] = [
    {
        "label": "Подписчики",
        "value": 142340,
        "delta": 2480,
        "percentDelta": 1.8,
        "positive": True,
    },
    {
        "label": "Ср. охват",
        "value": 38200,
        "percentDelta": 4.1,
        "positive": True,
    },
    {
        "label": "ER",
        "value": 26.9,
        "percentDelta": -1.2,
        "positive": False,
    },
    {
        "label": "Индекс цитирования",
        "value": 184,
        "delta": 9,
        "positive": True,
    },
]

MOCK_GROWTH_DATA: List[Dict[str, Any]] = [
    {"date": "01.06", "подписчики": 134200},
    {"date": "05.06", "подписчики": 135800},
    {"date": "10.06", "подписчики": 136400},
    {"date": "15.06", "подписчики": 137900},
    {"date": "20.06", "подписчики": 139100},
    {"date": "25.06", "подписчики": 140300},
    {"date": "30.06", "подписчики": 142340},
]

MOCK_POSTS: List[Dict[str, Any]] = [
    {
        "title": "Обзор нового iPhone 16 Pro",
        "views": 52100,
        "reactions": 890,
        "forwards": 234,
        "er": 31.2,
    },
    {
        "title": "Сравнение Android vs iOS в 2026",
        "views": 41300,
        "reactions": 756,
        "forwards": 189,
        "er": 28.4,
    },
    {
        "title": "Топ-10 приложений для продуктивности",
        "views": 38000,
        "reactions": 567,
        "forwards": 123,
        "er": 22.1,
    },
    {
        "title": "Как заработать на Telegram-канале",
        "views": 22400,
        "reactions": 198,
        "forwards": 45,
        "er": 14.8,
    },
]

MOCK_TARIFFS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Free",
        "description": "Для тех, кто начинает изучать Telegram-аналитику",
        "price": "0 ₽",
        "period": "навсегда",
        "monthlyPrice": 0,
        "features": [
            {"id": 1, "text": "Базовая статистика"},
            {"id": 2, "text": "5 AI-разборов / мес"},
            {"id": 3, "text": "Каталог каналов"},
        ],
        "button": {"label": "Начать бесплатно", "variant": "default"},
    },
    {
        "id": 2,
        "name": "Pro",
        "label": "Популярный",
        "description": "Для авторов и рекламодателей, которым важны данные",
        "price": "990 ₽",
        "period": "в месяц",
        "monthlyPrice": 990,
        "features": [
            {"id": 1, "text": "Всё из Free"},
            {"id": 2, "text": "Безлимит AI-разборов"},
            {"id": 3, "text": "Контент-план на неделю"},
            {"id": 4, "text": "Сравнение до 5 каналов"},
            {"id": 5, "text": "Экспорт отчётов"},
        ],
        "button": {"label": "Выбрать Pro", "variant": "primary"},
        "isHighlighted": True,
        "isPopular": True,
    },
    {
        "id": 3,
        "name": "Agency",
        "description": "Для агентств и команд, работающих с множеством каналов",
        "price": "4 900 ₽",
        "period": "в месяц",
        "monthlyPrice": 4900,
        "features": [
            {"id": 1, "text": "Всё из Pro"},
            {"id": 2, "text": "До 50 каналов"},
            {"id": 3, "text": "API-доступ"},
            {"id": 4, "text": "Командный доступ"},
        ],
        "button": {"label": "Выбрать Agency", "variant": "default"},
    },
]
