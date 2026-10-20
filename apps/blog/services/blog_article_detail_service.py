from typing import Optional

from django.db.models import Case, F, IntegerField, QuerySet, Value, When

from apps.blog.dto.blog_dto import (
    ArticleCardDTO,
    ArticleDetailDTO,
    CallToActionDTO,
)
from apps.blog.mock_data import as_card, get_mock_article, get_mock_cards
from apps.blog.models import BlogArticle
from apps.blog.services.mappers import to_article_card


class BlogArticleDetailService:
    """
    Собирает данные для страницы статьи блога
    (Inertia 'BlogPost', /blog/<slug>/).

    - build_mock(): моковый payload из реестра apps.blog.mock_data —
      используется вьюхой сейчас; slug вне реестра отдаёт
      featured-демо с подставленным slug;
    - build()/get_published_by_slug()/record_view(): работа с БД
      (оставлены для prod-переключения позже): отдаётся только
      опубликованная статья, для отсутствующей или неопубликованной
      вью отвечает 404.
    """

    CTA_LABEL = "Разобрать канал"
    CTA_URL = "/ai-cabinet"
    RELATED_LIMIT = 3

    def get_published_by_slug(self, slug: str) -> Optional[BlogArticle]:
        """Возвращает опубликованную статью по slug или None."""
        return (
            BlogArticle.objects.filter(slug=slug, is_published=True)
            .select_related("author")
            .first()
        )

    def build(self, article: BlogArticle) -> ArticleDetailDTO:
        """Собирает полный payload статьи для Inertia-страницы."""
        return ArticleDetailDTO(
            **to_article_card(article).model_dump(),
            body=article.body,
            cta=self._build_cta(),
            related=[
                to_article_card(item) for item in self._get_related(article)
            ],
        )

    def build_mock(self, slug: str) -> ArticleDetailDTO:
        """Моковый payload статьи из реестра для Inertia-страницы."""
        data = get_mock_article(slug)
        return ArticleDetailDTO(
            **as_card(data),
            body=data["body"],
            cta=self._build_cta(),
            related=[
                ArticleCardDTO(**card)
                for card in get_mock_cards(
                    exclude_slug=data["slug"], limit=self.RELATED_LIMIT
                )
            ],
        )

    def record_view(self, article: BlogArticle) -> None:
        """
        Увеличивает счётчик просмотров статьи.

        Отдельный UPDATE, поэтому кэш страницы не сбрасывается,
        а updated_at не меняется.
        """
        BlogArticle.objects.filter(pk=article.pk).update(
            views_count=F("views_count") + 1
        )

    # ------------------------
    # QuerySets
    # ------------------------

    def _get_related(self, article: BlogArticle) -> QuerySet[BlogArticle]:
        """
        Другие опубликованные статьи для блока «Читайте также».

        Сначала своя категория, затем остальные, по дате публикации.
        """
        return (
            BlogArticle.objects.filter(is_published=True)
            .exclude(pk=article.pk)
            .select_related("author")
            .annotate(
                is_same_category=Case(
                    When(category=article.category, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by("is_same_category", "-published_at", "-created_at")[
                : self.RELATED_LIMIT
            ]
        )

    # ------------------------
    # Mappers
    # ------------------------

    def _build_cta(self) -> CallToActionDTO:
        """Дескриптор кнопки-CTA внизу статьи."""
        return CallToActionDTO(label=self.CTA_LABEL, url=self.CTA_URL)
