import pytest

from apps.group_channels.services.collections_catalog_service import (
    CollectionsCatalogService,
)

pytest_plugins = ("apps.group_channels.test_utils",)
pytestmark = pytest.mark.django_db


@pytest.fixture
def catalog_service():
    """Сервис построения каталога подборок."""
    return CollectionsCatalogService()


class TestCollectionsCatalogService:
    """Тесты бизнес-логики каталога подборок."""

    def test_empty_catalog(self, catalog_service):
        """Пустой каталог не содержит подборок и секций."""
        result = catalog_service.build()

        assert result.collections == []
        assert result.featured == []
        assert result.sections == []
        assert result.filters.country_options == []
        assert result.filters.category_options == []

    def test_builds_collection_with_correct_data(
        self,
        catalog_service,
        group_factory,
        curator,
    ):
        """Сервис формирует DTO подборки с корректными данными."""
        group = group_factory(
            name="Топ IT-каналов",
            slug="top-it",
            description="Подборка технологических каналов",
            curator=curator,
            is_editorial=True,
            image_url="https://example.com/cover.jpg",
        )

        result = catalog_service.build()

        collection = next(
            item for item in result.collections if item.slug == group.slug
        )

        assert collection.id == group.pk
        assert collection.name == group.name
        assert collection.slug == group.slug
        assert collection.description == group.description
        assert collection.is_editorial is True
        assert collection.curator == curator.username
        assert collection.channel_count == 0
        assert collection.cover == group.image_url
        assert collection.gradient_key == f"collection-{group.pk}"

    def test_manual_group_counts_only_linked_channels(
        self,
        catalog_service,
        group_factory,
        channel_factory,
    ):
        """Ручная подборка считает только связанные с ней каналы."""
        group = group_factory(
            name="Топ IT-каналов",
            slug="top-it",
            is_editorial=True,
        )

        first_channel = channel_factory(
            username="product_radar",
            title="Product Radar",
            category="Технологии",
            country="RU",
        )
        second_channel = channel_factory(
            username="tech_news",
            title="Tech News",
            category="Технологии",
            country="RU",
        )

        group.channels.add(first_channel, second_channel)

        # Канал той же категории, который не добавлен в подборку.
        channel_factory(
            username="another_tech_channel",
            title="Another Tech Channel",
            category="Технологии",
            country="RU",
        )

        result = catalog_service.build()

        collection = next(
            item for item in result.collections if item.slug == group.slug
        )

        assert collection.channel_count == 2

    def test_auto_group_counts_channels_by_rule_category(
        self,
        catalog_service,
        group_factory,
        auto_rule_factory,
        channel_factory,
    ):
        """Автоподборка считает каналы категории своего правила."""
        group = group_factory(
            name="Научные каналы",
            slug="science",
        )
        auto_rule_factory(group, category="Наука")

        channel_factory(
            username="science_news",
            title="Science News",
            category="Наука",
        )
        channel_factory(
            username="science_today",
            title="Science Today",
            category="Наука",
        )
        channel_factory(
            username="product_radar",
            title="Product Radar",
            category="Технологии",
        )

        result = catalog_service.build()

        collection = next(
            item for item in result.collections if item.slug == group.slug
        )

        assert collection.channel_count == 2

    def test_featured_contains_at_most_three_collections(
        self,
        catalog_service,
        group_factory,
    ):
        """В featured попадает не больше трёх подборок."""
        group_factory(
            name="Топ IT-каналов",
            slug="top-it",
            is_editorial=True,
            order=0,
        )
        group_factory(
            name="Научные каналы",
            slug="science",
            is_editorial=True,
            order=1,
        )
        group_factory(
            name="Новости",
            slug="news",
            is_editorial=True,
            order=2,
        )
        group_factory(
            name="Игры",
            slug="games",
            order=3,
        )
        group_factory(
            name="Киберспорт",
            slug="cybersport",
            order=4,
        )

        result = catalog_service.build()

        assert len(result.featured) == 3
        assert [item.slug for item in result.featured] == [
            "top-it",
            "science",
            "news",
        ]

    def test_featured_prioritizes_editorial_collections(
        self,
        catalog_service,
        group_factory,
    ):
        """Редакторские подборки имеют приоритет в featured."""
        group_factory(
            name="Топ IT-каналов",
            slug="top-it",
            is_editorial=True,
            order=2,
        )
        group_factory(
            name="Научные каналы",
            slug="science",
            is_editorial=True,
            order=1,
        )
        group_factory(
            name="Новости",
            slug="news",
            is_editorial=False,
            order=0,
        )

        result = catalog_service.build()

        assert [item.slug for item in result.featured] == [
            "science",
            "top-it",
            "news",
        ]

    def test_collections_are_ordered_by_order_and_name(
        self,
        catalog_service,
        group_factory,
    ):
        """Подборки сортируются сначала по order, затем по name."""
        group_factory(
            name="Научные каналы",
            slug="science",
            order=1,
        )
        group_factory(
            name="Топ IT-каналов",
            slug="top-it",
            order=1,
        )
        group_factory(
            name="Новости",
            slug="news",
            order=0,
        )

        result = catalog_service.build()

        assert [item.slug for item in result.collections] == [
            "news",
            "science",
            "top-it",
        ]

    @pytest.mark.parametrize(
        ("query", "expected_slug"),
        [
            ("технолог", "top-it"),
            ("Новости", "news"),
        ],
    )
    def test_filters_by_search_query(
        self,
        catalog_service,
        group_factory,
        query,
        expected_slug,
    ):
        """Поиск сужает результаты по названию и описанию."""
        group_factory(
            name="Топ IT-каналов",
            slug="top-it",
            description="Подборка технологических каналов",
        )
        group_factory(
            name="Новости",
            slug="news",
            description="Актуальные события",
        )
        group_factory(
            name="Игры",
            slug="games",
            description="Подборка игровых каналов",
        )

        result = catalog_service.build(q=query)

        assert [item.slug for item in result.collections] == [expected_slug]
        assert result.filters.q == query

    def test_filters_by_country(
        self,
        catalog_service,
        group_factory,
        auto_rule_factory,
        channel_factory,
    ):
        """Фильтр страны учитывает ручные и автоматические подборки."""
        manual_group = group_factory(
            name="Игры",
            slug="games",
        )

        manual_group.channels.add(
            channel_factory(
                title="Игровой канал RU",
                category="Игры",
                country="RU",
            ),
            channel_factory(
                title="Игровой канал DE",
                category="Игры",
                country="DE",
            ),
        )

        auto_group = group_factory(
            name="Новости",
            slug="news",
        )
        auto_rule_factory(auto_group, category="Новости")

        channel_factory(
            title="Новостной канал RU",
            category="Новости",
            country="RU",
        )
        channel_factory(
            title="Новостной канал DE",
            category="Новости",
            country="DE",
        )

        result = catalog_service.build(country="RU")

        assert {item.slug for item in result.collections} == {
            "games",
            "news",
        }
        assert result.filters.country == "RU"
        assert result.filters.country_options == ["DE", "RU"]
        assert result.filters.category_options == ["Игры", "Новости"]

    def test_filters_by_category(
        self,
        catalog_service,
        group_factory,
        auto_rule_factory,
        channel_factory,
    ):
        """Фильтр категории учитывает ручные и автоматические подборки."""
        games_group = group_factory(
            name="Игры",
            slug="games",
        )

        games_group.channels.add(
            channel_factory(
                title="Игровой канал RU",
                category="Игры",
                country="RU",
            ),
            channel_factory(
                title="Игровой канал DE",
                category="Игры",
                country="DE",
            ),
        )

        news_group = group_factory(
            name="Новости",
            slug="news",
        )
        auto_rule_factory(news_group, category="Новости")

        channel_factory(
            title="Новостной канал RU",
            category="Новости",
            country="RU",
        )

        result = catalog_service.build(category="Игры")

        assert [item.slug for item in result.collections] == ["games"]
        assert result.filters.category == "Игры"
        assert result.filters.country_options == ["DE", "RU"]
        assert result.filters.category_options == ["Игры", "Новости"]

    def test_builds_sections_from_collection_categories(
        self,
        catalog_service,
        group_factory,
        auto_rule_factory,
        channel_factory,
    ):
        """Секции формируются по категориям ручных и автоподборок."""
        manual_group = group_factory(
            name="Топ IT-каналов",
            slug="top-it",
        )

        manual_group.channels.add(
            channel_factory(
                title="IT-канал",
                category="Технологии",
            ),
            channel_factory(
                title="Киберспортивный канал",
                category="Киберспорт",
            ),
        )

        auto_group = group_factory(
            name="Научные каналы",
            slug="science",
        )
        auto_rule_factory(auto_group, category="Наука")

        result = catalog_service.build()

        sections_by_title = {
            section.title: section for section in result.sections
        }

        assert set(sections_by_title) == {
            "Технологии",
            "Киберспорт",
            "Наука",
        }

        assert sections_by_title["Технологии"].count == 1
        assert sections_by_title["Киберспорт"].count == 1
        assert sections_by_title["Наука"].count == 1

        assert [
            item.slug for item in sections_by_title["Технологии"].collections
        ] == ["top-it"]

        assert [
            item.slug for item in sections_by_title["Наука"].collections
        ] == ["science"]
