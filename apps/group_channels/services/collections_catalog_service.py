from django.db.models import Count

from apps.group_channels.dto.collections_dto import (
    CollectionDTO,
    CollectionsCatalogDTO,
)
from apps.group_channels.models import Group
from apps.parser.models import TelegramChannel


class CollectionsCatalogService:
    """Формирует данные публичного каталога подборок."""

    def build(self) -> CollectionsCatalogDTO:
        groups = list(
            Group.objects.select_related(
                "owner",
                "curator",
                "auto_rule",
            )
            .prefetch_related("channels")
            .order_by("order", "name", "id")
        )

        self._annotate_channel_counts(groups)

        # Редакторские подборки имеют приоритет(?).
        # Затем сортировка по order и id.
        featured_groups = sorted(
            groups,
            key=lambda group: (
                not group.is_editorial,
                group.order,
                group.id,
            ),
        )[:3]

        collections = [self._build_collection(group) for group in groups]

        featured = [self._build_collection(group) for group in featured_groups]

        return CollectionsCatalogDTO(
            featured=featured,
            collections=collections,
        )

    @staticmethod
    def _annotate_channel_counts(groups: list[Group]) -> None:
        """
        Рассчитывает количество каналов для каждой группы.

        Обычные группы используют M2M Group.channels.

        Автоматические группы определяют каналы по категории
        из AutoGroupRule.

        Для автоматических групп категории считаются одним
        aggregate-запросом, поэтому N+1 запросов не возникает.
        """

        categories = {
            group.auto_rule.category
            for group in groups
            if hasattr(group, "auto_rule")
        }

        category_counts: dict[str, int] = {}

        if categories:
            for row in (
                TelegramChannel.objects.filter(category__in=categories)
                .values("category")
                .annotate(total=Count("pk"))
            ):
                category = row["category"]

                if category is not None:
                    category_counts[category] = row["total"]

        for group in groups:
            if hasattr(group, "auto_rule"):
                setattr(
                    group,
                    "annotated_channel_count",
                    category_counts.get(
                        group.auto_rule.category,
                        0,
                    ),
                )
            else:
                # channels уже загружены через prefetch_related(),
                # поэтому отдельный запрос для каждой группы не выполняется.
                setattr(
                    group,
                    "annotated_channel_count",
                    len(group.channels.all()),
                )

    @staticmethod
    def _build_collection(group: Group) -> CollectionDTO:
        """Преобразует Group в DTO публичного каталога."""

        data = group.get_data()

        # Ключ должен быть стабильным:
        # одна и та же подборка всегда получает один и тот же ключ.
        data["gradient_key"] = f"collection-{group.pk}"

        return CollectionDTO.model_validate(data)
