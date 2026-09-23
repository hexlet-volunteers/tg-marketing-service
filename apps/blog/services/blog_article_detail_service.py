from typing import Optional

from django.db.models import Case, F, IntegerField, QuerySet, Value, When

from apps.blog.dto.blog_dto import ArticleDetailDTO, CallToActionDTO
from apps.blog.models import BlogArticle
from apps.blog.services.mappers import to_article_card


class BlogArticleDetailService:
    """
    Собирает данные для страницы статьи блога
    (Inertia 'BlogArticle', /blog/<slug>/).

    Отдаётся только опубликованная статья (is_published=True);
    для отсутствующей или неопубликованной вью отвечает 404.
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
