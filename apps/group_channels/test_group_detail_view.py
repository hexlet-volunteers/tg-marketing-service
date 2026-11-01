import json
from typing import Any

import pytest
from django.http import HttpResponse
from django.urls import reverse

pytest_plugins = ("apps.group_channels.test_utils",)
pytestmark = pytest.mark.django_db


@pytest.fixture
def catalog_url():
    """URL каталога подборок."""
    return reverse("collections_catalog")


@pytest.fixture
def detail_url():
    """Функция построения URL детальной страницы подборки."""

    def factory(slug):
        return reverse("collection_detail", kwargs={"slug": slug})

    return factory


def get_inertia_props(response: HttpResponse) -> dict[str, Any]:
    """Возвращает props из Inertia-ответа."""
    assert response.status_code == 200

    page: dict[str, Any] = json.loads(response.content)

    assert "props" in page

    props = page["props"]
    assert isinstance(props, dict)

    return props


class TestCollectionsCatalogView:
    """Функциональные тесты HTTP-контракта каталога."""

    def test_catalog_returns_inertia_page(
        self,
        client,
        catalog_url,
    ):
        """Каталог возвращает компонент Collections и необходимые props."""
        response = client.get(
            catalog_url,
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert response.json()["component"] == "Collections"

        assert isinstance(props["featured"], list)
        assert isinstance(props["collections"], list)
        assert isinstance(props["sections"], list)
        assert isinstance(props["filters"], dict)

    def test_catalog_serializes_manual_group_channel_count(
        self,
        client,
        catalog_url,
        manual_group,
    ):
        """Каталог передаёт рассчитанный счётчик ручной подборки."""
        response = client.get(
            catalog_url,
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        collection = next(
            item
            for item in props["collections"]
            if item["slug"] == manual_group.slug
        )

        assert collection["channel_count"] == 1

    def test_catalog_serializes_auto_group_channel_count(
        self,
        client,
        catalog_url,
        auto_group,
        channel_factory,
    ):
        """Каталог передаёт рассчитанный счётчик автоподборки."""
        expected_channels = [
            channel_factory(
                title="Science News",
                username="science_news",
                category="Наука",
            ),
            channel_factory(
                title="Science Today",
                username="science_today",
                category="Наука",
            ),
        ]

        channel_factory(
            title="Product Radar",
            username="product_radar",
            category="Технологии",
        )

        response = client.get(
            catalog_url,
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        collection = next(
            item
            for item in props["collections"]
            if item["slug"] == auto_group.slug
        )

        assert collection["channel_count"] == len(expected_channels)

    def test_empty_catalog_returns_empty_lists(
        self,
        client,
        catalog_url,
    ):
        """Пустой каталог сериализуется с пустыми списками."""
        response = client.get(
            catalog_url,
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert props["collections"] == []
        assert props["featured"] == []
        assert props["sections"] == []

    @pytest.mark.parametrize(
        ("query_params", "filter_key", "filter_value"),
        [
            (
                {"q": "технолог"},
                "q",
                "технолог",
            ),
            (
                {"country": "RU"},
                "country",
                "RU",
            ),
            (
                {"category": "Технологии"},
                "category",
                "Технологии",
            ),
        ],
        ids=["search", "country", "category"],
    )
    def test_catalog_applies_query_filters(
        self,
        client,
        catalog_url,
        group_factory,
        channel_factory,
        query_params,
        filter_key,
        filter_value,
    ):
        """HTTP-параметры фильтрации влияют на выдачу каталога."""
        tech_group = group_factory(
            name="Топ IT-каналов",
            slug="top-it",
            description="Подборка технологических каналов",
        )
        tech_group.channels.add(
            channel_factory(
                title="Product Radar",
                username="product_radar",
                category="Технологии",
                country="RU",
            ),
        )

        news_group = group_factory(
            name="Новости",
            slug="news",
            description="Актуальные события",
        )
        news_group.channels.add(
            channel_factory(
                title="News Channel",
                username="news_channel",
                category="Новости",
                country="DE",
            ),
        )

        response = client.get(
            catalog_url,
            query_params,
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert [item["slug"] for item in props["collections"]] == [
            tech_group.slug
        ]

        assert props["filters"][filter_key] == filter_value

        # Дополнительно убеждаемся, что неподходящая подборка исключена.
        assert news_group.slug not in {
            item["slug"] for item in props["collections"]
        }


class TestGroupDetailView:
    """Функциональные тесты HTTP-контракта детальной страницы."""

    def test_detail_returns_inertia_page(
        self,
        client,
        detail_url,
        manual_group,
    ):
        """Детальная страница возвращает GroupDetail и необходимые props."""
        response = client.get(
            detail_url(manual_group.slug),
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert response.json()["component"] == "GroupDetail"

        assert "header" in props
        assert "group" in props
        assert "channels" in props
        assert "auto_category" in props

        assert isinstance(props["header"], dict)
        assert isinstance(props["group"], dict)
        assert isinstance(props["channels"], list)

    def test_detail_returns_correct_header(
        self,
        client,
        detail_url,
        manual_group,
    ):
        """Заголовок содержит данные ручной подборки."""
        response = client.get(
            detail_url(manual_group.slug),
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)
        header = props["header"]

        assert header["name"] == manual_group.name
        assert header["description"] == manual_group.description
        assert header["gradient_key"] == (f"collection-{manual_group.pk}")
        assert header["is_editorial"] is True
        assert header["category"] is None
        assert header["channel_count"] == 1

    def test_detail_returns_group_data(
        self,
        client,
        detail_url,
        manual_group,
    ):
        """Props group содержит данные выбранной подборки."""
        response = client.get(
            detail_url(manual_group.slug),
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)
        group = props["group"]

        assert group["id"] == manual_group.pk
        assert group["name"] == manual_group.name
        assert group["slug"] == manual_group.slug
        assert group["description"] == manual_group.description
        assert group["is_editorial"] is True
        assert group["channel_count"] == 1

    def test_detail_returns_channel_cards(
        self,
        client,
        detail_url,
        manual_group,
    ):
        """Каналы ручной подборки сериализуются в карточки."""
        response = client.get(
            detail_url(manual_group.slug),
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert props["channels"] == [
            {
                "title": "Product Radar",
                "username": "product_radar",
                "avatar": "",
                "subscribers": 142000,
                "average_views": 38200,
                "category": "Технологии",
                "country": "RU",
            }
        ]

        assert props["header"]["channel_count"] == len(props["channels"])

    def test_detail_returns_curator(
        self,
        client,
        detail_url,
        group_factory,
        curator,
    ):
        """Куратор передаётся в заголовке и данных подборки."""
        group = group_factory(
            name="Топ IT-каналов",
            slug="top-it",
            curator=curator,
        )

        response = client.get(
            detail_url(group.slug),
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert props["header"]["curator"] == curator.username
        assert props["group"]["curator"] == curator.username

    def test_auto_group_returns_category(
        self,
        client,
        detail_url,
        auto_group,
    ):
        """Для автоподборки передаётся категория правила."""
        response = client.get(
            detail_url(auto_group.slug),
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert props["auto_category"] == "Наука"
        assert props["header"]["category"] == "Наука"

    def test_auto_group_returns_only_channels_of_its_category(
        self,
        client,
        detail_url,
        auto_group,
        channel_factory,
    ):
        """Автоподборка содержит каналы категории своего правила."""
        expected_channel = channel_factory(
            title="Научный канал",
            username="science_channel",
            category="Наука",
        )

        channel_factory(
            title="IT-канал",
            username="product_radar",
            category="Технологии",
        )

        response = client.get(
            detail_url(auto_group.slug),
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert len(props["channels"]) == 1
        assert props["channels"][0]["title"] == expected_channel.title
        assert props["channels"][0]["category"] == "Наука"
        assert props["header"]["channel_count"] == 1

    def test_empty_manual_group_returns_empty_channels(
        self,
        client,
        detail_url,
        group_factory,
    ):
        """Ручная подборка без каналов возвращает пустой список."""
        group = group_factory(
            name="Топ IT-каналов",
            slug="top-it",
        )

        response = client.get(
            detail_url(group.slug),
            HTTP_X_INERTIA="true",
        )

        props = get_inertia_props(response)

        assert props["channels"] == []
        assert props["header"]["channel_count"] == 0

    def test_unknown_slug_returns_404(
        self,
        client,
        detail_url,
    ):
        """Несуществующая подборка возвращает 404."""
        response = client.get(
            detail_url("unknown-collection"),
            HTTP_X_INERTIA="true",
        )

        assert response.status_code == 404
