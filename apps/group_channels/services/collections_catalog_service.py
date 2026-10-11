from collections import defaultdict

from django.db.models import Count, Exists, OuterRef, Prefetch, Q, QuerySet

from apps.group_channels.dto.collections_dto import (
    CollectionDTO,
    CollectionsCatalogDTO,
    CollectionSectionDTO,
    CollectionsFiltersDTO,
)
from apps.group_channels.models import Group
from apps.parser.models import TelegramChannel


class CollectionsCatalogService:
    """
    Сервис формирования публичного каталога подборок.

    Поддерживает фильтрацию по названию/описанию, стране и категории,
    формирует featured, полный список коллекций и секции по категориям.
    """

    def build(
        self,
        q: str | None = None,
        country: str | None = None,
        category: str | None = None,
    ) -> CollectionsCatalogDTO:
        """Собирает каталог с применёнными фильтрами."""

        groups_qs = self._get_groups()

        groups = list(
            self._filter_groups(
                groups_qs,
                q=q,
                country=country,
                category=category,
            )
        )

        self._annotate_channel_counts(groups)

        collection_map = {
            group.id: self._build_collection(group) for group in groups
        }

        collections = list(collection_map.values())

        featured_groups = sorted(
            groups,
            key=lambda group: (
                not group.is_editorial,
                group.order,
                group.id,
            ),
        )[:3]

        featured = [collection_map[group.id] for group in featured_groups]

        sections = self._build_sections(
            groups,
            collection_map,
        )

        country_options, category_options = self._get_filter_options(
            groups_qs,
            q=q,
            country=country,
            category=category,
        )

        return CollectionsCatalogDTO(
            featured=featured,
            collections=collections,
            sections=sections,
            filters=CollectionsFiltersDTO(
                q=q,
                country=country,
                category=category,
                country_options=country_options,
                category_options=category_options,
            ),
        )

    @staticmethod
    def _get_groups() -> QuerySet[Group]:
        """Возвращает подборки со связанными данными."""

        channels_qs = TelegramChannel.objects.only(
            "id",
            "category",
            "country",
        )

        return (
            Group.objects.select_related(
                "owner",
                "curator",
                "auto_rule",
            )
            .prefetch_related(
                Prefetch(
                    "channels",
                    queryset=channels_qs,
                ),
            )
            .order_by(
                "order",
                "name",
                "id",
            )
        )

    @staticmethod
    def _filter_groups(
        groups: QuerySet[Group],
        *,
        q: str | None,
        country: str | None,
        category: str | None,
    ) -> QuerySet[Group]:
        """Фильтрует подборки по поиску, стране и категории."""

        if q:
            groups = groups.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        if country:
            regular_channels = TelegramChannel.objects.filter(
                groups=OuterRef("pk"),
                country=country,
            )

            auto_channels = TelegramChannel.objects.filter(
                category=OuterRef("auto_rule__category"),
                country=country,
            )

            groups = groups.annotate(
                has_matching_regular_channel=Exists(
                    regular_channels,
                ),
                has_matching_auto_channel=Exists(
                    auto_channels,
                ),
            ).filter(
                Q(
                    auto_rule__isnull=True,
                    has_matching_regular_channel=True,
                )
                | Q(
                    auto_rule__isnull=False,
                    has_matching_auto_channel=True,
                )
            )

        if category:
            regular_category_channels = TelegramChannel.objects.filter(
                groups=OuterRef("pk"),
                category=category,
            )

            groups = groups.annotate(
                has_matching_category_channel=Exists(
                    regular_category_channels,
                ),
            ).filter(
                Q(
                    auto_rule__isnull=True,
                    has_matching_category_channel=True,
                )
                | Q(
                    auto_rule__isnull=False,
                    auto_rule__category=category,
                )
            )

        return groups

    @staticmethod
    def _annotate_channel_counts(groups: list[Group]) -> None:
        """
        Рассчитывает количество каналов для каждой группы.

        Для обычных групп используется M2M Group.channels.

        Для auto-групп количество каналов определяется
        по категории из AutoGroupRule.

        Для auto-групп все категории собираются заранее,
        поэтому отдельного COUNT-запроса на каждую группу нет.
        """

        auto_categories = {
            group.auto_rule.category
            for group in groups
            if group.is_auto and group.auto_rule.category
        }

        category_counts: dict[str, int] = {}

        if auto_categories:
            for row in (
                TelegramChannel.objects.filter(category__in=auto_categories)
                .values("category")
                .annotate(total=Count("pk"))
            ):
                category = row["category"]

                if category is not None:
                    category_counts[category] = row["total"]

        for group in groups:
            if group.is_auto:
                setattr(
                    group,
                    "annotated_channel_count",
                    category_counts.get(group.auto_rule.category, 0),
                )
            else:
                setattr(
                    group,
                    "annotated_channel_count",
                    len(group.channels.all()),
                )

    @staticmethod
    def _build_collection(group: Group) -> CollectionDTO:
        """Преобразует Group в DTO коллекции."""

        data = group.get_data()
        data["gradient_key"] = f"collection-{group.pk}"

        return CollectionDTO.model_validate(data)

    @staticmethod
    def _build_sections(
        groups: list[Group],
        collection_map: dict[int, CollectionDTO],
    ) -> list[CollectionSectionDTO]:
        """Группирует коллекции по категориям."""

        sections: dict[str, list[CollectionDTO]] = defaultdict(list)

        for group in groups:
            collection = collection_map[group.id]

            if group.is_auto:
                categories = (
                    {group.auto_rule.category}
                    if group.auto_rule.category
                    else set()
                )
            else:
                categories = {
                    channel.category
                    for channel in group.channels.all()
                    if channel.category
                }

            for category in categories:
                sections[category].append(collection)

        return [
            CollectionSectionDTO(
                title=title,
                collections=section_collections,
                count=len(section_collections),
            )
            for title, section_collections in sorted(
                sections.items(),
                key=lambda item: item[0],
            )
        ]

    @staticmethod
    def _get_filter_options(
        groups: QuerySet[Group],
        *,
        q: str | None,
        country: str | None,
        category: str | None,
    ) -> tuple[list[str], list[str]]:
        """Возвращает доступные значения фильтров с учетом остальных фильтров.

        Для country учитываются подборки, отфильтрованные по q и category,
        при этом текущий country игнорируется.

        Для category учитываются подборки, отфильтрованные по q и country,
        при этом текущий category игнорируется.

        Для auto-подборок категория берется из AutoGroupRule, а страны —
        из реальных каналов соответствующей категории.
        """
        country_groups = CollectionsCatalogService._filter_groups(
            groups,
            q=q,
            country=None,
            category=category,
        )

        category_groups = CollectionsCatalogService._filter_groups(
            groups,
            q=q,
            country=country,
            category=None,
        )

        regular_country_groups = country_groups.filter(
            auto_rule__isnull=True,
        )

        auto_country_categories = country_groups.filter(
            auto_rule__isnull=False
        ).values_list(
            "auto_rule__category",
            flat=True,
        )

        country_values = (
            TelegramChannel.objects.filter(
                Q(groups__in=regular_country_groups)
                | Q(category__in=auto_country_categories)
            )
            .values_list("country", flat=True)
            .distinct()
        )

        regular_category_groups = category_groups.filter(
            auto_rule__isnull=True,
        )

        category_values = (
            TelegramChannel.objects.filter(groups__in=regular_category_groups)
            .values_list("category", flat=True)
            .distinct()
        )

        auto_category_values = (
            category_groups.filter(auto_rule__isnull=False)
            .values_list(
                "auto_rule__category",
                flat=True,
            )
            .distinct()
        )

        countries = sorted(filter(None, country_values))

        categories = sorted(
            set(filter(None, category_values))
            | set(filter(None, auto_category_values))
        )

        return countries, categories
