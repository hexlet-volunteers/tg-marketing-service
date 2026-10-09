from django.test import TestCase

from apps.group_channels.models import AutoGroupRule, Group
from apps.group_channels.services.collections_catalog_service import (
    CollectionsCatalogService,
)
from apps.parser.models import TelegramChannel
from apps.users.models import User


class CollectionsCatalogServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ivan",
            email="ivan@test.ru",
            password="123",
            role="user",
        )
        self.service = CollectionsCatalogService()

    def test_empty_catalog(self):
        """Проверяет, что пустой каталог возвращает пустые списки."""
        result = self.service.build()

        self.assertEqual(result.collections, [])
        self.assertEqual(result.featured, [])

    def test_build_collection(self):
        """Проверяет, что подборка содержит все данные каталога."""
        curator = User.objects.create_user(
            username="curator",
            email="curator@test.ru",
            password="123",
            role="user",
        )

        group = Group.objects.create(
            name="Игры",
            owner=self.user,
            curator=curator,
            description="Игровые каналы",
            is_editorial=True,
            image_url="https://example.com/cover.jpg",
        )

        result = self.service.build()
        collection = result.collections[0]

        self.assertEqual(collection.id, group.id)
        self.assertEqual(collection.name, group.name)
        self.assertEqual(collection.slug, group.slug)
        self.assertEqual(collection.description, group.description)
        self.assertTrue(collection.is_editorial)
        self.assertEqual(collection.curator, curator.username)
        self.assertEqual(collection.channel_count, 0)
        self.assertEqual(collection.cover, group.image_url)
        self.assertEqual(
            collection.gradient_key,
            f"collection-{group.id}",
        )

    def test_channel_count(self):
        """Проверяет корректный подсчёт каналов
        для обычной и автоматической подборок."""

        # Создаём обычную подборку с каналами через M2M-связь.
        regular_group = Group.objects.create(
            name="Игры",
            owner=self.user,
        )
        # Создаём автоматическую подборку, каналы которой
        # определяются по категории из AutoGroupRule.
        auto_group = Group.objects.create(
            name="Новости",
            owner=self.user,
        )
        AutoGroupRule.objects.create(
            group=auto_group,
            category="Новости",
        )

        # Создаём два канала, которые добавим в обычную подборку.
        channel_1 = TelegramChannel.objects.create(
            channel_id=1001,
            title="Игры 1",
            category="Игры",
        )
        channel_2 = TelegramChannel.objects.create(
            channel_id=1002,
            title="Игры 2",
            category="Игры",
        )

        regular_group.channels.add(channel_1, channel_2)

        # Эти каналы имеют ту же категорию, но не добавлены в M2M.
        # Для проверки, что обычная подборка считает
        # только связанные с ней каналы.
        TelegramChannel.objects.create(
            channel_id=1003,
            title="Игры 3",
            category="Игры",
        )
        TelegramChannel.objects.create(
            channel_id=1004,
            title="Новости 1",
            category="Новости",
        )
        TelegramChannel.objects.create(
            channel_id=1005,
            title="Новости 2",
            category="Новости",
        )

        # Проверяем, что сервис не выполняет дополнительные запросы
        # для каждой подборки и канала.
        with self.assertNumQueries(6):
            result = self.service.build()

        collections = {
            collection.id: collection for collection in result.collections
        }

        self.assertEqual(
            collections[regular_group.id].channel_count,
            2,
        )
        self.assertEqual(
            collections[auto_group.id].channel_count,
            2,
        )

    def test_featured(self):
        """Проверяет сортировку и приоритет редакторских
        подборок."""
        Group.objects.create(
            name="Обычная первая",
            owner=self.user,
            order=1,
            is_editorial=False,
        )
        Group.objects.create(
            name="Обычная вторая",
            owner=self.user,
            order=2,
            is_editorial=False,
        )
        editorial_first = Group.objects.create(
            name="Редакторская первая",
            owner=self.user,
            order=2,
            is_editorial=True,
        )
        editorial_second = Group.objects.create(
            name="Редакторская вторая",
            owner=self.user,
            order=1,
            is_editorial=True,
        )
        editorial_third = Group.objects.create(
            name="Редакторская третья",
            owner=self.user,
            order=3,
            is_editorial=True,
        )
        Group.objects.create(
            name="Обычная третья",
            owner=self.user,
            order=3,
            is_editorial=False,
        )

        result = self.service.build()

        self.assertEqual(len(result.featured), 3)
        self.assertEqual(
            [item.id for item in result.featured],
            [
                editorial_second.id,
                editorial_first.id,
                editorial_third.id,
            ],
        )

    def test_collections(self):
        """Проверяет сортировку полного списка подборок
        по order, name и id."""
        first = Group.objects.create(
            name="А",
            owner=self.user,
            order=1,
        )
        second = Group.objects.create(
            name="Б",
            owner=self.user,
            order=1,
        )
        third = Group.objects.create(
            name="В",
            owner=self.user,
            order=2,
        )

        result = self.service.build()

        self.assertEqual(
            [item.id for item in result.collections],
            [first.id, second.id, third.id],
        )

    def test_filter_by_query(self):
        """Проверяет фильтр подборки по названию и описанию."""
        name_match = Group.objects.create(
            name="Игры",
            owner=self.user,
            description="Каналы про развлечения",
        )
        description_match = Group.objects.create(
            name="Новости",
            owner=self.user,
            description="Подборка про Игры и киберспорт",
        )
        Group.objects.create(
            name="Финансы",
            owner=self.user,
            description="Экономика и инвестиции",
        )

        result = self.service.build(q="Игры")

        self.assertEqual(
            [item.id for item in result.collections],
            [name_match.id, description_match.id],
        )

    def test_filter_by_country(self):
        """Фильтрует обычные и автоматические подборки по стране."""
        regular_group = Group.objects.create(
            name="Игры",
            owner=self.user,
        )
        auto_group = Group.objects.create(
            name="Новости",
            owner=self.user,
        )

        # Не попадает в подборку.
        Group.objects.create(
            name="Спорт",
            owner=self.user,
        )

        AutoGroupRule.objects.create(
            group=auto_group,
            category="Новости",
        )

        regular_group.channels.add(
            TelegramChannel.objects.create(
                channel_id=1001,
                title="Игры RU",
                category="Игры",
                country="RU",
            ),
        )

        regular_group.channels.add(
            TelegramChannel.objects.create(
                channel_id=1002,
                title="Игры DE",
                category="Игры",
                country="DE",
            ),
        )

        TelegramChannel.objects.create(
            channel_id=1003,
            title="Новости RU",
            category="Новости",
            country="RU",
        )

        TelegramChannel.objects.create(
            channel_id=1004,
            title="Новости DE",
            category="Новости",
            country="DE",
        )

        result = self.service.build(country="RU")

        self.assertEqual(
            [item.id for item in result.collections],
            [regular_group.id, auto_group.id],
        )

        self.assertEqual(
            result.filters.country,
            "RU",
        )

        self.assertEqual(
            result.filters.country_options,
            ["DE", "RU"],
        )

        self.assertEqual(
            result.filters.category_options,
            ["Игры", "Новости"],
        )

    def test_filter_by_category(self):
        """Фильтрует обычные и автоматические подборки по категории."""
        games_group = Group.objects.create(
            name="Игры",
            owner=self.user,
        )
        news_group = Group.objects.create(
            name="Новости",
            owner=self.user,
        )

        Group.objects.create(
            name="Спорт",
            owner=self.user,
        )

        games_group.channels.add(
            TelegramChannel.objects.create(
                channel_id=1001,
                title="Игры RU",
                category="Игры",
                country="RU",
            ),
            TelegramChannel.objects.create(
                channel_id=1002,
                title="Игры DE",
                category="Игры",
                country="DE",
            ),
        )

        AutoGroupRule.objects.create(
            group=news_group,
            category="Новости",
        )

        result = self.service.build(category="Игры")

        self.assertEqual(
            [item.id for item in result.collections],
            [games_group.id],
        )

        self.assertEqual(
            result.filters.category,
            "Игры",
        )

        self.assertEqual(
            result.filters.country_options,
            ["DE", "RU"],
        )

        self.assertEqual(
            result.filters.category_options,
            ["Игры", "Новости"],
        )

    def test_sections(self):
        """Проверяет группировку подборок по категориям каналов."""
        games = Group.objects.create(
            name="Игры",
            owner=self.user,
        )
        news = Group.objects.create(
            name="Новости",
            owner=self.user,
        )

        AutoGroupRule.objects.create(
            group=news,
            category="Новости",
        )

        games_rpg = TelegramChannel.objects.create(
            channel_id=1001,
            title="RPG",
            category="Игры",
        )
        games_esports = TelegramChannel.objects.create(
            channel_id=1002,
            title="Esports",
            category="Киберспорт",
        )

        games.channels.add(
            games_rpg,
            games_esports,
        )

        TelegramChannel.objects.create(
            channel_id=1003,
            title="Новости",
            category="Новости",
        )

        result = self.service.build()

        sections = {section.title: section for section in result.sections}

        self.assertEqual(
            [item.id for item in sections["Игры"].collections],
            [games.id],
        )
        self.assertEqual(
            [item.id for item in sections["Киберспорт"].collections],
            [games.id],
        )
        self.assertEqual(
            [item.id for item in sections["Новости"].collections],
            [news.id],
        )

        self.assertEqual(sections["Игры"].count, 1)
        self.assertEqual(sections["Киберспорт"].count, 1)
        self.assertEqual(sections["Новости"].count, 1)
