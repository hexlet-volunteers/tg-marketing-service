from typing import Optional

from django.db.models import QuerySet

from apps.blog.dto.blog_dto import BlogListDTO
from apps.blog.models import BlogArticle
from apps.blog.services.mappers import to_article_card


class BlogListService:
    """
    Собирает данные для страницы списка блога (Inertia 'Blog', /blog/).

    Возвращает:
    - featured: последняя опубликованная статья с is_featured=True;
    - articles: все остальные опубликованные статьи (без featured),
      отсортированные по published_at desc.
    """

    def build(self) -> BlogListDTO:
        featured = self._get_featured_article()
        articles_qs = self._get_articles_queryset(featured)

        return BlogListDTO(
            featured=to_article_card(featured) if featured else None,
            articles=[to_article_card(article) for article in articles_qs],
        )

    # ------------------------
    # QuerySets
    # ------------------------

    def _get_featured_article(self) -> Optional[BlogArticle]:
        return (
            BlogArticle.objects.filter(is_published=True, is_featured=True)
            .order_by("-published_at", "-created_at")
            .select_related("author")
            .first()
        )

    def _get_articles_queryset(
        self, featured: Optional[BlogArticle]
    ) -> QuerySet[BlogArticle]:
        qs = BlogArticle.objects.filter(is_published=True).select_related(
            "author"
        )
        if featured is not None:
            qs = qs.exclude(pk=featured.pk)
        return qs.order_by("-published_at", "-created_at")
